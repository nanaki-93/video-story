"""Verified disposable payloads with fixed paths, atomic writes and bounded pruning."""

import errno
import hashlib
import os
import shutil
import stat
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from pydantic import TypeAdapter

from ..assets.service import digest_file
from ..documents import parse_document
from ..models.base import SHA256, HashedFile, MediaPath, canonical_bytes, content_hash
from ..models.cache import (
    CACHE_PREFIX,
    CacheEntry,
    CacheInventory,
    CacheKind,
    CachePruneReport,
    CacheSummary,
)
from ..persistence import ProjectBusy, StorageError, UnsafePath


class CacheStore:
    def __init__(self, store):
        self.store = store

    @staticmethod
    def identity(kind, key):
        kind = TypeAdapter(CacheKind).validate_python(kind)
        key = TypeAdapter(SHA256).validate_python(key)
        return f"{CACHE_PREFIX}/{kind}/{key}"

    @staticmethod
    def payload_name(kind):
        return "payload.png" if kind == "normalized_image" else "payload.mp4"

    @staticmethod
    def _digest_at(directory, name):
        descriptor = os.open(name, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW, dir_fd=directory)
        with os.fdopen(descriptor, "rb") as stream:
            before = os.fstat(stream.fileno())
            if not stat.S_ISREG(before.st_mode):
                raise UnsafePath("cache payload must be a regular file")
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
            after = os.fstat(stream.fileno())
            if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
                raise StorageError("cache payload changed while being read")
            return digest, after.st_size

    def _read_entry(self, directory, kind, key):
        entry = parse_document(self.store._read_at(directory, "entry.json"))
        if not isinstance(entry, CacheEntry) or (entry.kind, entry.key) != (kind, key):
            raise StorageError("cache entry identity differs from its path")
        return entry

    def lookup(self, kind, descriptor, *, destination=None):
        """Return a verified entry; optionally create a new owned working copy/link."""
        key = content_hash(descriptor)
        relative = self.identity(kind, key)
        try:
            with self.store.exclusive_lock(".tabi-cache.lock"):
                with self.store._directory(self.store._parts(relative)) as directory:
                    entry = self._read_entry(directory, kind, key)
                    if entry.descriptor != descriptor or self._digest_at(
                        directory, self.payload_name(kind)
                    ) != (
                        entry.output.sha256,
                        entry.output.size_bytes,
                    ):
                        return None
                    if destination is not None:
                        self._export_at(
                            directory, self.payload_name(kind), Path(destination), entry
                        )
                    return entry
        except UnsafePath:
            raise
        except (FileNotFoundError, ValueError, ProjectBusy):
            return None
        except OSError as error:
            if error.errno == errno.ELOOP:
                raise UnsafePath("cache payload is a symlink") from error
            raise

    def _export_at(self, directory, name, destination, entry):
        try:
            if entry.kind == "video_chunk":
                # Resumable job artifacts need independent bytes; callers can
                # truncate a failed job without poisoning the shared cache.
                raise OSError(errno.EXDEV, "copy video into its owned job")
            os.link(name, destination, src_dir_fd=directory, follow_symlinks=False)
        except OSError as error:
            if error.errno != errno.EXDEV:
                raise
            descriptor = os.open(name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=directory)
            created = False
            try:
                with os.fdopen(descriptor, "rb") as source, destination.open("xb") as output:
                    created = True
                    shutil.copyfileobj(source, output, length=1024 * 1024)
                    output.flush()
                    os.fsync(output.fileno())
                if digest_file(destination) != (entry.output.sha256, entry.output.size_bytes):
                    raise StorageError("cache copy changed during export")
            except BaseException:
                # This destination is a new, caller-owned working path.
                if created:
                    destination.unlink(missing_ok=True)
                raise

    def put(self, kind, descriptor, source, *, report=None, warnings=(), refresh=False):
        key = content_hash(descriptor)
        relative = self.identity(kind, key)
        source = Path(source)
        expected_hash, expected_size = digest_file(source)
        try:
            with self.store.exclusive_lock(".tabi-cache.lock"):
                with self.store._directory(self.store._parts(relative), create=True) as directory:
                    name = self.payload_name(kind)
                    try:
                        previous = self._read_entry(directory, kind, key)
                        if not refresh and self._digest_at(directory, name) == (
                            previous.output.sha256,
                            previous.output.size_bytes,
                        ):
                            return previous
                    except UnsafePath:
                        raise
                    except (FileNotFoundError, ValueError):
                        pass
                    for target in (name, "entry.json"):
                        try:
                            info = os.stat(target, dir_fd=directory, follow_symlinks=False)
                            if not stat.S_ISREG(info.st_mode):
                                raise UnsafePath("refusing to replace a non-file cache entry")
                        except FileNotFoundError:
                            pass
                    if name in os.listdir(directory):
                        path = f"{relative}/{name}"
                        if any(
                            path == p or path.startswith(p + "/") for p in self._protected_paths()
                        ):
                            return None  # A disposable file became an authored source; preserve it.
                    temporary = f".payload-{uuid4().hex}.tmp"
                    try:
                        fd = os.open(
                            temporary,
                            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                            0o600,
                            dir_fd=directory,
                        )
                        # A cache entry owns independent bytes. Editing an old job artifact
                        # must not mutate a valid cache payload through a shared hard link.
                        with source.open("rb") as original, os.fdopen(fd, "wb") as output:
                            shutil.copyfileobj(original, output, length=1024 * 1024)
                            output.flush()
                            os.fsync(output.fileno())
                        if self._digest_at(directory, temporary) != (expected_hash, expected_size):
                            raise StorageError("cache payload copy failed verification")
                        entry = CacheEntry(
                            schema_version="1.0",
                            kind=kind,
                            key=key,
                            descriptor=descriptor,
                            created_at=datetime.now(UTC),
                            report=report,
                            warnings=list(warnings),
                            output=HashedFile(
                                location=MediaPath(path=f"{relative}/{name}"),
                                sha256=expected_hash,
                                size_bytes=expected_size,
                            ),
                        )
                        os.replace(temporary, name, src_dir_fd=directory, dst_dir_fd=directory)
                        os.fsync(directory)
                        self.store._atomic_write(
                            f"{relative}/entry.json", canonical_bytes(entry), overwrite=True
                        )
                        return entry
                    finally:
                        try:
                            os.unlink(temporary, dir_fd=directory)
                        except FileNotFoundError:
                            pass
        except ProjectBusy:
            return None  # Contention may cost a cache fill, never a valid render.

    def _protected_paths(self):
        protected = set()

        def visit(data):
            if isinstance(data, dict):
                if data.get("root_id") == "project" and isinstance(data.get("path"), str):
                    protected.add(data["path"])
                for child in data.values():
                    visit(child)
            elif isinstance(data, list):
                for child in data:
                    visit(child)

        def scan(parts):
            try:
                with self.store._directory(parts) as directory:
                    for name in os.listdir(directory):
                        info = os.stat(name, dir_fd=directory, follow_symlinks=False)
                        if stat.S_ISLNK(info.st_mode):
                            raise UnsafePath("metadata symlink prevents safe cache pruning")
                        if stat.S_ISDIR(info.st_mode):
                            scan((*parts, name))
                        elif name.endswith(".json"):
                            visit(self.store.read("/".join((*parts, name))).model_dump(mode="json"))
            except FileNotFoundError:
                return

        for folder in ("registry", "snapshots", "episodes", "releases"):
            scan((folder,))
        return protected

    def _inventory(self):
        protected = self._protected_paths()
        entries, warnings = [], []
        for kind in ("normalized_image", "video_chunk"):
            base = f"{CACHE_PREFIX}/{kind}"
            try:
                with self.store._directory(self.store._parts(base)) as directory:
                    keys = sorted(os.listdir(directory))
            except FileNotFoundError:
                continue
            for key in keys:
                try:
                    relative = self.identity(kind, key)
                    with self.store._directory(self.store._parts(relative)) as directory:
                        entry = self._read_entry(directory, kind, key)
                        try:
                            digest, size = self._digest_at(directory, self.payload_name(kind))
                            valid = (digest, size) == (entry.output.sha256, entry.output.size_bytes)
                            message = None if valid else "Payload hash or size changed."
                        except FileNotFoundError:
                            size, valid, message = 0, False, "Payload is missing."
                        path = entry.output.location.path
                        pinned = any(path == p or path.startswith(p + "/") for p in protected)
                        entries.append(
                            CacheSummary(
                                kind=kind,
                                key=key,
                                size_bytes=size,
                                sha256=entry.output.sha256,
                                created_at=entry.created_at,
                                valid=valid,
                                message=message,
                                protected=pinned,
                            )
                        )
                except (ValueError, OSError) as error:
                    warnings.append(f"Unrecognized cache entry {kind}/{key} was preserved: {error}")
        entries.sort(key=lambda entry: (entry.kind, entry.key))
        return CacheInventory(
            schema_version="1.0",
            root=str(self.store.root / CACHE_PREFIX),
            entries=entries,
            inventory_sha256=content_hash(
                {"entries": [e.model_dump(mode="json") for e in entries], "warnings": warnings}
            ),
            entry_bytes=sum(entry.size_bytes for entry in entries),
            warnings=warnings,
        )

    def inventory(self):
        with self.store.exclusive_lock(".tabi-cache.lock"):
            return self._inventory()

    def prune(self, keys, *, expected_inventory):
        keys = TypeAdapter(list[SHA256]).validate_python(keys)
        if len(keys) != len(set(keys)):
            raise ValueError("cache prune keys must be unique")
        with (
            self.store.exclusive_lock(".tabi-worker.lock"),
            self.store.writer_lock(),
            self.store.exclusive_lock(".tabi-cache.lock"),
        ):
            inventory = self._inventory()
            if inventory.inventory_sha256 != expected_inventory:
                raise StorageError("cache inventory changed; inspect it again before pruning")
            selected = [entry for entry in inventory.entries if entry.key in keys]
            if len(selected) != len(keys) or any(entry.protected for entry in selected):
                raise StorageError(
                    "prune selection is unknown or referenced as source media; nothing removed"
                )
            removed = 0
            for entry in selected:
                relative = self.identity(entry.kind, entry.key)
                with self.store._directory(self.store._parts(relative)) as directory:
                    # Delete only these two owned files. Unknown files and directories
                    # are retained; no recursive deletion can reach source or snapshots.
                    for name in (self.payload_name(entry.kind), "entry.json"):
                        try:
                            info = os.stat(name, dir_fd=directory, follow_symlinks=False)
                            if not stat.S_ISREG(info.st_mode):
                                raise UnsafePath(
                                    "cache entry changed to a non-file; pruning stopped"
                                )
                            os.unlink(name, dir_fd=directory)
                        except FileNotFoundError:
                            pass
                    os.fsync(directory)
                removed += entry.size_bytes
                parts = self.store._parts(relative)
                with self.store._directory(parts[:-1]) as parent:
                    try:
                        os.rmdir(parts[-1], dir_fd=parent)
                    except OSError as error:
                        if error.errno not in {errno.ENOENT, errno.ENOTEMPTY}:
                            raise
            return CachePruneReport(
                schema_version="1.0",
                removed=keys,
                removed_entry_bytes=removed,
                remaining_entry_bytes=inventory.entry_bytes - removed,
            )
