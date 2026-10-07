"""POSIX project storage: bounded paths, one writer, atomic drafts and frozen snapshots.

Locks coordinate application writers. Directory descriptors and O_NOFOLLOW keep
metadata operations from following symlinks. This is not an OS sandbox against
another process with permission to modify the user's project directory.
"""

import copy
import errno
import fcntl
import hashlib
import os
import re
import stat
from collections.abc import Callable, Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from .documents import MAX_DOCUMENT_BYTES, decode_data, parse_document, validate_data
from .models import CompiledSnapshot, Project
from .models.assets import ApprovableDocument
from .models.base import (
    Document,
    DraftDocument,
    MediaPath,
    canonical_bytes,
    relative_path,
    version_tuple,
)


class StorageError(ValueError):
    pass


class UnsafePath(StorageError):
    pass


class ProjectBusy(StorageError):
    pass


class RevisionConflict(StorageError):
    pass


class ImmutableDocument(StorageError):
    pass


def resolve_media_path(
    reference: MediaPath, project_root: Path, allowed_media_roots: Mapping[str, Path]
) -> Path:
    """Resolve against trusted launcher roots, not roots asserted by an imported document."""
    reference = MediaPath.model_validate(reference)
    if reference.root_id == "project":
        root = project_root.resolve()
    else:
        if reference.root_id not in allowed_media_roots:
            raise UnsafePath(f"media root is not registered: {reference.root_id}")
        root = allowed_media_roots[reference.root_id].resolve()
    try:
        candidate = (root / reference.path).resolve()
    except (OSError, RuntimeError) as error:
        raise UnsafePath("media path cannot be resolved") from error
    if not candidate.is_relative_to(root):
        raise UnsafePath("media path escapes its registered root through a symlink")
    return candidate


def document_path(document: DraftDocument) -> str:
    kind = document.document_type
    if kind == "project":
        return "project.json"
    folders = {
        "app_preferences": "preferences",
        "preview_selection": "previews",
        "episode": "episodes",
        "render_job": "jobs",
        "release_record": "releases",
        "release_preparation": "publishing",
    }
    if kind in folders:
        return f"{folders[kind]}/{document.id}.json"
    versioned = {
        "asset": "assets",
        "scene_template": "templates",
        "action_pack": "actions",
    }
    if kind in versioned:
        return f"registry/{versioned[kind]}/{document.id}/{document.version}.json"
    raise ImmutableDocument("this document type is not a mutable draft")


@dataclass(frozen=True)
class Migration:
    source: str
    target: str
    transform: Callable[[dict], dict]


class MigrationRegistry:
    """Explicit forward migrations within major 1; no invented legacy conversions."""

    def __init__(self) -> None:
        self.steps: dict[str, Migration] = {}

    def register(self, source: str, target: str, transform: Callable[[dict], dict]) -> None:
        old, new = version_tuple(source), version_tuple(target)
        if old[0] != 1 or new[0] != 1 or new <= old:
            raise StorageError("migrations must move forward within supported major 1")
        if source in self.steps:
            raise StorageError("migration source already registered")
        self.steps[source] = Migration(source, target, transform)

    def plan(self, source: str, target: str) -> list[Migration]:
        old, new = version_tuple(source), version_tuple(target)
        if old[0] != 1 or new[0] != 1 or new <= old:
            raise StorageError("migration needs a newer target within supported major 1")
        result = []
        current = source
        while current != target:
            step = self.steps.get(current)
            if step is None or version_tuple(step.target) > new:
                raise StorageError(f"no registered migration from {current} to {target}")
            result.append(step)
            current = step.target
        return result


class ProjectStore:
    def __init__(self, root: Path):
        self.root = root.expanduser().resolve()
        if not self.root.is_dir():
            raise FileNotFoundError(f"project directory does not exist: {self.root}")

    @contextmanager
    def _directory(self, parts: tuple[str, ...], *, create: bool = False) -> Iterator[int]:
        descriptor = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            for part in parts:
                if create:
                    try:
                        os.mkdir(part, mode=0o700, dir_fd=descriptor)
                    except FileExistsError:
                        pass
                child = os.open(
                    part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor
                )
                os.close(descriptor)
                descriptor = child
            yield descriptor
        except OSError as error:
            if error.errno in {errno.ELOOP, errno.ENOTDIR}:
                raise UnsafePath("metadata path contains a symlink or non-directory") from error
            raise
        finally:
            os.close(descriptor)

    @contextmanager
    def writer_lock(self) -> Iterator[None]:
        with self.exclusive_lock(".tabi.lock"):
            yield

    @contextmanager
    def exclusive_lock(self, relative: str) -> Iterator[None]:
        """Nonblocking process lease; the inode remains in place after release."""
        parts = self._parts(relative)
        with self._directory(parts[:-1], create=True) as directory:
            descriptor = os.open(
                parts[-1], os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600, dir_fd=directory
            )
        try:
            if not stat.S_ISREG(os.fstat(descriptor).st_mode) or os.fstat(descriptor).st_nlink != 1:
                raise UnsafePath("project lock must be a regular, unshared file")
            try:
                fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as error:
                raise ProjectBusy(
                    "another writer owns this project; retry after it finishes"
                ) from error
            yield
        finally:
            # Keep the lock inode on disk: unlinking allows two independent locks.
            os.close(descriptor)

    @staticmethod
    def _parts(relative: str) -> tuple[str, ...]:
        try:
            return tuple(relative_path(relative).split("/"))
        except ValueError as error:
            raise UnsafePath(str(error)) from error

    @staticmethod
    def _read_at(directory: int, name: str) -> bytes:
        descriptor = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
        with os.fdopen(descriptor, "rb") as source:
            if not stat.S_ISREG(os.fstat(source.fileno()).st_mode):
                raise UnsafePath("document must be a regular file")
            payload = source.read(MAX_DOCUMENT_BYTES + 1)
            if len(payload) > MAX_DOCUMENT_BYTES:
                raise StorageError("document exceeds 16 MiB")
            return payload

    def _read_bytes(self, relative: str) -> bytes:
        parts = self._parts(relative)
        with self._directory(parts[:-1]) as directory:
            return self._read_at(directory, parts[-1])

    def read(self, relative: str = "project.json") -> Document:
        parts = self._parts(relative)
        if parts[0] == "snapshots":
            if len(parts) != 2 or not parts[1].endswith(".json"):
                raise UnsafePath("snapshot must be addressed by its SHA-256 filename")
            return self.read_snapshot(parts[1][:-5])
        return parse_document(self._read_bytes(relative))

    def _atomic_write(self, relative: str, payload: bytes, *, overwrite: bool) -> None:
        parts = self._parts(relative)
        with self._directory(parts[:-1], create=True) as directory:
            try:
                target = os.stat(parts[-1], dir_fd=directory, follow_symlinks=False)
                if not stat.S_ISREG(target.st_mode):
                    raise UnsafePath("refusing to replace a symlink or non-file document")
            except FileNotFoundError:
                pass
            temporary = f".{parts[-1]}.{uuid4().hex}.tmp"
            try:
                descriptor = os.open(
                    temporary,
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                    0o600,
                    dir_fd=directory,
                )
                with os.fdopen(descriptor, "wb") as destination:
                    destination.write(payload)
                    destination.flush()
                    os.fsync(destination.fileno())
                if self._read_at(directory, temporary) != payload:
                    raise StorageError("temporary document failed byte verification")
                if overwrite:
                    os.replace(temporary, parts[-1], src_dir_fd=directory, dst_dir_fd=directory)
                else:
                    # Atomic no-clobber publication for new files, backups and snapshots.
                    os.link(
                        temporary,
                        parts[-1],
                        src_dir_fd=directory,
                        dst_dir_fd=directory,
                        follow_symlinks=False,
                    )
                os.fsync(directory)
            finally:
                try:
                    os.unlink(temporary, dir_fd=directory)
                except FileNotFoundError:
                    pass

    def _backup(self, relative: str, payload: bytes, label: str) -> Path:
        backup = f".backups/{relative}.{label}.{uuid4().hex}.bak"
        self._atomic_write(backup, payload, overwrite=False)
        return self.root / backup

    @classmethod
    def initialize(cls, root: Path, title: str) -> "ProjectStore":
        # Validate user input before creating anything.
        now = datetime.now(UTC).isoformat()
        document = validate_data(
            {
                "schema_version": "1.0",
                "document_type": "project",
                "id": str(uuid4()),
                "title": title,
                "created_at": now,
                "updated_at": now,
            }
        )
        root = root.expanduser().resolve()
        root.mkdir(parents=True, exist_ok=True)
        if any(path.name != ".tabi.lock" for path in root.iterdir()):
            raise StorageError(
                "project init requires an empty directory; existing files are preserved"
            )
        store = cls(root)
        with store.writer_lock():
            if any(path.name != ".tabi.lock" for path in root.iterdir()):
                raise StorageError(
                    "project init requires an empty directory; existing files are preserved"
                )
            for folder in (
                "episodes",
                "registry",
                "assets",
                "audio",
                "rights",
                "sources",
                "snapshots",
                "exports",
                ".cache",
            ):
                with store._directory((folder,), create=True):
                    pass
            store._atomic_write("project.json", canonical_bytes(document), overwrite=False)
        return store

    def save_draft(
        self, document: DraftDocument, *, expected_revision: int | None
    ) -> DraftDocument:
        validated = validate_data(document.model_dump(mode="json"))
        if not isinstance(validated, DraftDocument) or isinstance(validated, CompiledSnapshot):
            raise ImmutableDocument("use save_snapshot for immutable compiler output")
        relative = document_path(validated)
        if expected_revision is not None and (
            type(expected_revision) is not int or expected_revision < 0
        ):
            raise RevisionConflict(
                "expected_revision must be a nonnegative integer or null for creation"
            )
        with self.writer_lock():
            try:
                previous_bytes = self._read_bytes(relative)
            except FileNotFoundError:
                previous_bytes = None
            data = validated.model_dump(mode="json")
            if previous_bytes is None:
                if expected_revision is not None or validated.revision != 0:
                    raise RevisionConflict("new drafts require no expected revision and revision 0")
            else:
                previous = parse_document(previous_bytes)
                if (
                    isinstance(previous, ApprovableDocument)
                    and previous.approval.status == "approved"
                ):
                    raise ImmutableDocument(
                        "approved versions cannot be edited; create a new version"
                    )
                if (
                    not isinstance(previous, DraftDocument)
                    or previous.id != validated.id
                    or previous.document_type != validated.document_type
                ):
                    raise StorageError("document identity cannot change in place")
                if document_path(previous) != relative:
                    raise StorageError("stored document identity does not match its path")
                if (
                    expected_revision != previous.revision
                    or validated.revision != expected_revision
                ):
                    raise RevisionConflict(
                        f"stale revision; current revision is {previous.revision}"
                    )
                data["revision"] = previous.revision + 1
                if isinstance(previous, Project):
                    data["created_at"] = previous.created_at.isoformat()
                    data["updated_at"] = datetime.now(UTC).isoformat()
                self._backup(relative, previous_bytes, f"revision-{previous.revision}")
            updated = validate_data(data)
            self._atomic_write(
                relative, canonical_bytes(updated), overwrite=previous_bytes is not None
            )
        return updated

    def save_snapshot(self, document: CompiledSnapshot) -> str:
        validated = validate_data(document.model_dump(mode="json"))
        if not isinstance(validated, CompiledSnapshot):
            raise ImmutableDocument("save_snapshot accepts only compiled snapshots")
        payload = canonical_bytes(validated)
        digest = hashlib.sha256(payload).hexdigest()
        relative = f"snapshots/{digest}.json"
        with self.writer_lock():
            try:
                existing = self._read_bytes(relative)
            except FileNotFoundError:
                existing = None
            if existing is not None:
                if existing != payload:
                    raise ImmutableDocument(
                        "snapshot path contains altered data; refusing to overwrite"
                    )
            else:
                self._atomic_write(relative, payload, overwrite=False)
        return digest

    def read_snapshot(self, digest: str) -> CompiledSnapshot:
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise UnsafePath("snapshot ID must be a lowercase SHA-256")
        payload = self._read_bytes(f"snapshots/{digest}.json")
        if hashlib.sha256(payload).hexdigest() != digest:
            raise ImmutableDocument("snapshot content does not match its immutable identity")
        document = parse_document(payload)
        if not isinstance(document, CompiledSnapshot):
            raise ImmutableDocument("snapshot path contains a different document type")
        return document

    def migrate(
        self,
        relative: str,
        *,
        expected_revision: int,
        target_version: str,
        target_model: type[DraftDocument],
        migrations: MigrationRegistry,
    ) -> DraftDocument:
        parts = self._parts(relative)
        if parts[0] == "snapshots":
            raise ImmutableDocument("snapshots must never be migrated in place")
        if type(expected_revision) is not int or expected_revision < 0:
            raise RevisionConflict("expected revision must be a nonnegative integer")
        with self.writer_lock():
            original = self._read_bytes(relative)
            data = decode_data(original)
            if data.get("document_type") == "compiled_snapshot" or (
                isinstance(data.get("approval"), dict)
                and data["approval"].get("status") == "approved"
            ):
                raise ImmutableDocument("approved documents cannot be migrated in place")
            if type(data.get("revision")) is not int or data["revision"] != expected_revision:
                raise RevisionConflict("migration revision is stale or missing")
            steps = migrations.plan(data.get("schema_version"), target_version)
            # Back up exact bytes before invoking any transformation, including failures.
            self._backup(
                relative, original, f"migration-{data['schema_version']}-to-{target_version}"
            )
            transformed = copy.deepcopy(data)
            for step in steps:
                transformed = step.transform(transformed)
                if (
                    not isinstance(transformed, dict)
                    or transformed.get("schema_version") != step.target
                ):
                    raise StorageError("migration did not produce its declared target version")
            for key in ("document_type", "id", "version", "revision"):
                if transformed.get(key) != data.get(key):
                    raise StorageError(f"migration cannot change {key}")
            if (
                isinstance(transformed.get("approval"), dict)
                and transformed["approval"].get("status") == "approved"
            ):
                raise ImmutableDocument("migration cannot approve a draft")
            transformed["revision"] = expected_revision + 1
            migrated = validate_data(transformed, model=target_model)
            if not isinstance(migrated, DraftDocument) or isinstance(migrated, CompiledSnapshot):
                raise ImmutableDocument("migration target must be a mutable draft")
            if document_path(migrated) != relative:
                raise UnsafePath("migration cannot change a document's storage identity")
            self._atomic_write(relative, canonical_bytes(migrated), overwrite=True)
        return migrated
