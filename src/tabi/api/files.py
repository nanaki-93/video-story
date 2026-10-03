"""Bounded chooser and descriptor-based, verified artifact byte ranges."""

import hashlib
import os
import re
import stat
import threading
from contextlib import contextmanager
from pathlib import Path

from pydantic import TypeAdapter
from starlette.responses import Response, StreamingResponse

from tabi.core.models.base import Identifier, relative_path
from tabi.core.persistence import ProjectStore, UnsafePath

from .contracts import FileEntry, WebDirectory, WebRoot, WebRoots


class FileStreamResponse(StreamingResponse):
    def __init__(self, *args, close, **kwargs):
        super().__init__(*args, **kwargs)
        self.close_file = close

    async def __call__(self, scope, receive, send):
        try:
            await super().__call__(scope, receive, send)
        finally:
            self.close_file()


class RootRegistry:
    def __init__(self, roots):
        self.roots = {}
        for identity, root in roots.items():
            TypeAdapter(Identifier).validate_python(identity)
            if identity == "project":
                raise ValueError("root ID project is reserved")
            resolved = Path(root).expanduser().resolve(strict=True)
            if not resolved.is_dir():
                raise ValueError("registered root must be an existing directory")
            self.roots[identity] = resolved

    def listing(self):
        return WebRoots(
            schema_version="1.0",
            roots=[WebRoot(id=key, path=str(path)) for key, path in self.roots.items()],
        )

    def root(self, identity):
        if identity not in self.roots:
            raise UnsafePath("unregistered local root")
        return self.roots[identity]

    def directory(self, identity, relative=""):
        root = self.root(identity)
        parts = tuple(relative_path(relative).split("/")) if relative else ()
        # Every directory component is opened without following symlinks.
        with ProjectStore(root)._directory(parts):
            result = root.joinpath(*parts)
            if not result.resolve(strict=True).is_relative_to(root):
                raise UnsafePath("folder escaped its registered root")
            return result

    def browse(self, identity, relative="", offset=0):
        parts = tuple(relative_path(relative).split("/")) if relative else ()
        entries = []
        with ProjectStore(self.root(identity))._directory(parts) as descriptor:
            names = sorted(name for name in os.listdir(descriptor) if not name.startswith("."))
            for name in names[offset : offset + 200]:
                item = os.stat(name, dir_fd=descriptor, follow_symlinks=False)
                if not (stat.S_ISREG(item.st_mode) or stat.S_ISDIR(item.st_mode)):
                    continue
                path = "/".join((*parts, name))
                try:
                    relative_path(path)
                except ValueError:
                    continue
                entries.append(
                    FileEntry(
                        name=name,
                        path=path,
                        kind="directory" if stat.S_ISDIR(item.st_mode) else "file",
                        size_bytes=item.st_size if stat.S_ISREG(item.st_mode) else None,
                    )
                )
        return WebDirectory(
            schema_version="1.0",
            root_id=identity,
            path=relative,
            entries=entries,
            next_offset=offset + 200 if offset + 200 < len(names) else None,
        )


def byte_range(header, size):
    if not header:
        return 0, size
    match = re.fullmatch(r"bytes=(\d*)-(\d*)", header)
    if not match or not any(match.groups()):
        raise ValueError("unsupported range")
    first, last = match.groups()
    if first:
        start, end = int(first), min(size, int(last) + 1) if last else size
    else:
        start, end = max(0, size - int(last)), size
    if not 0 <= start < end <= size:
        raise ValueError("unsatisfied range")
    return start, end


@contextmanager
def open_local(store, relative):
    parts = store._parts(relative)
    with store._directory(parts[:-1]) as directory:
        descriptor = os.open(
            parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory
        )
    with os.fdopen(descriptor, "rb") as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise UnsafePath("artifact must be a regular file")
        yield stream


class Artifacts:
    def __init__(self):
        self.verified = {}
        self.lock = threading.Lock()

    def response(self, store, relative, expected, request, *, media_type="video/mp4"):
        context = open_local(store, relative)
        source = context.__enter__()
        closed = False

        def close():
            nonlocal closed
            if not closed:
                closed = True
                context.__exit__(None, None, None)

        try:
            info = os.fstat(source.fileno())
            stamp = (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)
            if expected:
                with self.lock:
                    if self.verified.get(stamp) != expected:
                        digest = hashlib.sha256()
                        for block in iter(lambda: source.read(1024 * 1024), b""):
                            digest.update(block)
                        after = os.fstat(source.fileno())
                        if digest.hexdigest() != expected or (info.st_size, info.st_mtime_ns) != (
                            after.st_size,
                            after.st_mtime_ns,
                        ):
                            raise ValueError("registered artifact bytes changed")
                        if len(self.verified) > 1024:
                            self.verified.clear()
                        self.verified[stamp] = expected
            try:
                first, end = byte_range(request.headers.get("range"), info.st_size)
            except ValueError:
                close()
                return Response(
                    status_code=416, headers={"Content-Range": f"bytes */{info.st_size}"}
                )
            headers = {"Accept-Ranges": "bytes", "Content-Length": str(end - first)}
            partial = request.headers.get("range") is not None
            if partial:
                headers["Content-Range"] = f"bytes {first}-{end - 1}/{info.st_size}"
            if request.method == "HEAD":
                close()
                return Response(
                    status_code=206 if partial else 200, headers=headers, media_type=media_type
                )
            source.seek(first)

            def chunks():
                try:
                    remaining = end - first
                    while remaining:
                        block = source.read(min(256 * 1024, remaining))
                        if not block:
                            raise OSError("artifact truncated during streaming")
                        yield block
                        remaining -= len(block)
                finally:
                    close()

            return FileStreamResponse(
                chunks(),
                close=close,
                status_code=206 if partial else 200,
                headers=headers,
                media_type=media_type,
            )
        except BaseException:
            close()
            raise
