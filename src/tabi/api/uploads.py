"""Resumable bounded copies. Incomplete bytes are never an asset or a render input."""

import hashlib
import os
import shutil
from uuid import uuid4

from tabi.core.models.base import MediaPath, canonical_bytes
from tabi.core.persistence import RevisionConflict

from .contracts import BeginUpload, WebUpload
from .files import open_local

CHUNK_BYTES = 4 * 1024**2


class Uploads:
    def __init__(self, store):
        self.store = store

    def _folder(self, identity):
        # Upload identities cannot name any existing project/source/cache directory.
        if len(identity) != 32 or any(c not in "0123456789abcdef" for c in identity):
            raise ValueError("invalid upload identity")
        return f".imports/{identity}"

    def start(self, request: BeginUpload):
        if "/" in request.name or request.name == "upload.json":
            raise ValueError("select a file, not a path")
        if shutil.disk_usage(self.store.root).free < request.size_bytes * 2 + CHUNK_BYTES:
            raise ValueError("insufficient space for staging and a verified source copy")
        result = WebUpload(
            schema_version="1.0",
            id=uuid4().hex,
            name=request.name,
            size_bytes=request.size_bytes,
            received_bytes=0,
        )
        folder = self._folder(result.id)
        with self.store.writer_lock():
            self.store._atomic_write(
                f"{folder}/upload.json", canonical_bytes(result), overwrite=False
            )
            self.store._atomic_write(f"{folder}/{result.name}", b"", overwrite=False)
        return result

    def read(self, identity):
        result = WebUpload.model_validate_json(
            self.store._read_bytes(f"{self._folder(identity)}/upload.json")
        )
        with open_local(self.store, f"{self._folder(identity)}/{result.name}") as source:
            size = os.fstat(source.fileno()).st_size
        if size < result.received_bytes or size > result.size_bytes:
            raise ValueError("upload staging changed; discard it and select the file again")
        # A process can stop after bytes are flushed and before their receipt is saved.
        # Unacknowledged bytes are checked against the next retry, never silently trusted.
        return result

    def chunk(self, identity, offset, data):
        if not 0 < len(data) <= CHUNK_BYTES or type(offset) is not int or offset < 0:
            raise ValueError("upload chunks need a nonnegative offset and at most 4 MiB")
        folder = self._folder(identity)
        with self.store.writer_lock():
            result = self.read(identity)
            if offset > result.received_bytes or offset + len(data) > result.size_bytes:
                raise RevisionConflict("upload offset differs from the acknowledged bytes")
            parts = self.store._parts(f"{folder}/{result.name}")
            with self.store._directory(parts[:-1]) as parent:
                fd = os.open(parts[-1], os.O_RDWR | os.O_NOFOLLOW, dir_fd=parent)
            with os.fdopen(fd, "r+b") as output:
                output.seek(offset)
                existing = output.read(len(data))
                if existing and not data.startswith(existing):
                    raise ValueError("selected file differs from the interrupted upload")
                output.seek(offset)
                output.write(data)
                output.flush()
                os.fsync(output.fileno())
            count = max(result.received_bytes, offset + len(data))
            updated = WebUpload(**{**result.model_dump(), "received_bytes": count})
            self.store._atomic_write(
                f"{folder}/upload.json", canonical_bytes(updated), overwrite=True
            )
            return updated

    def finish(self, identity):
        folder = self._folder(identity)
        with self.store.writer_lock():
            result = self.read(identity)
            if result.received_bytes != result.size_bytes:
                raise ValueError("upload is incomplete; reselect the same file to resume")
            with open_local(self.store, f"{folder}/{result.name}") as source:
                digest = hashlib.file_digest(source, "sha256").hexdigest()
            if result.sha256 is not None and digest != result.sha256:
                raise ValueError("completed upload bytes changed")
            updated = WebUpload(**{**result.model_dump(), "complete": True, "sha256": digest})
            self.store._atomic_write(
                f"{folder}/upload.json", canonical_bytes(updated), overwrite=True
            )
            return updated

    def location(self, identity):
        result = self.finish(identity)
        return MediaPath(path=f"{self._folder(identity)}/{result.name}")

    def discard(self, identity):
        folder = self._folder(identity)
        with self.store.writer_lock():
            result = self.read(identity)
            with self.store._directory(tuple(folder.split("/"))) as descriptor:
                for name in (result.name, "upload.json"):
                    os.unlink(name, dir_fd=descriptor)
            with self.store._directory((".imports",)) as parent:
                os.rmdir(identity, dir_fd=parent)
        return result
