"""Verified, atomic, no-clobber document copies outside the mutable project index."""

import os
from pathlib import Path
from tempfile import NamedTemporaryFile

from .documents import parse_document
from .models.base import Document, canonical_bytes
from .persistence import StorageError


def export_document(document: Document, output: Path) -> None:
    output = output.expanduser().absolute()
    if output.exists() or output.is_symlink():
        raise StorageError("document export exists; select a new path")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with NamedTemporaryFile(
            prefix=".tabi-document-", dir=output.parent, delete=False
        ) as stream:
            temporary = Path(stream.name)
            stream.write(canonical_bytes(document))
            stream.flush()
            os.fsync(stream.fileno())
        if parse_document(temporary.read_bytes()) != document:
            raise StorageError("document export failed byte/model verification")
        os.link(temporary, output)
        descriptor = os.open(output.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
