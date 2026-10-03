"""Streamed private directory backups with checked copies and atomic restore publication."""

import hashlib
import os
import shutil
import stat
import tempfile
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel

from .assets import AssetService
from .authoring import AuthoringService
from .jobs.ledger import JobLedger
from .models import ReleaseRecord
from .models.assets import ActionPack
from .models.base import AssetRef, HashedFile, MediaPath, canonical_bytes, relative_path
from .models.portability import BackupManifest, PortableRoots
from .models.publishing import ReleasePreparation
from .persistence import ProjectStore, StorageError
from .process import checkpoint

EXCLUDED = {".cache", ".imports", ".git", ".DS_Store"}
ROOTS_FILE = ".portable-roots.json"


@contextmanager
def source_file(store, relative):
    parts = store._parts(relative)
    with store._directory(parts[:-1]) as parent:
        fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
    with os.fdopen(fd, "rb") as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise StorageError("backup inputs must be regular files, never symlinks or devices")
        yield stream


def tree_files(store, relative="", *, exclude=True):
    parts = store._parts(relative) if relative else ()
    found = []
    with store._directory(parts) as parent:
        for name in sorted(os.listdir(parent)):
            if exclude and (
                name in EXCLUDED or name.startswith(".tabi-") or name.endswith(".lock")
            ):
                continue
            path = "/".join((*parts, name))
            relative_path(path)
            mode = os.stat(name, dir_fd=parent, follow_symlinks=False).st_mode
            if stat.S_ISDIR(mode):
                found.extend(tree_files(store, path, exclude=exclude))
            elif stat.S_ISREG(mode):
                found.append(path)
            else:
                raise StorageError(f"Backup refuses symlink or special file: {path}")
    return found


def transfer(store, relative, output=None, expected=None):
    """Hash the held descriptor; an optional target is always a fresh owned scratch file."""
    digest, count = hashlib.sha256(), 0
    with source_file(store, relative) as source:
        before = os.fstat(source.fileno())
        if output:
            output.parent.mkdir(parents=True, exist_ok=True)
            destination = output.open("xb")
        else:
            destination = None
        try:
            while block := source.read(1024 * 1024):
                checkpoint()
                digest.update(block)
                count += len(block)
                if destination:
                    destination.write(block)
            if destination:
                destination.flush()
                os.fsync(destination.fileno())
        finally:
            if destination:
                destination.close()
        after = os.fstat(source.fileno())
        if (before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (
            after.st_size,
            after.st_mtime_ns,
            after.st_ctime_ns,
        ):
            raise StorageError("backup input changed while copying")
    result = digest.hexdigest(), count
    if expected is not None and result != expected:
        raise StorageError(f"Backup file hash or size differs: {relative}")
    return result


def references(value):
    if isinstance(value, MediaPath):
        yield value
    elif isinstance(value, BaseModel):
        for item in value.__dict__.values():
            yield from references(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from references(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from references(item)


def check_project(store, expected_id=None):
    assets = AssetService(store)
    if expected_id is not None and store.read().id != expected_id:
        raise StorageError("restored project identity differs from the manifest")
    for asset in assets.list_assets():
        assets.require_valid(AssetRef(id=asset.id, version=asset.version))
    catalog = AuthoringService(assets)
    catalog.episodes()
    catalog.templates()
    catalog.documents("registry/actions", ActionPack)
    catalog.documents("releases", ReleaseRecord)
    catalog.documents("publishing", ReleasePreparation)
    for path in (store.root / "snapshots").glob("*.json"):
        store.read_snapshot(path.stem)
    if any(j.state in {"queued", "running"} for j in JobLedger(store).all()):
        raise StorageError("Pause or finish queued/running jobs before creating a portable backup")
    return assets


@contextmanager
def publication(destination, *, outside):
    destination = Path(destination)
    name = relative_path(destination.name)
    parent = destination.parent.resolve(strict=True)
    if parent.is_relative_to(outside.resolve()):
        raise StorageError("choose a new destination outside the source project or backup")
    target = parent / name
    if target.exists() or target.is_symlink():
        raise StorageError("backup/restore destination exists; select a new folder")
    scratch = Path(tempfile.mkdtemp(prefix=".tabi-portable-", dir=parent))
    reserved = False
    try:
        yield scratch
        for folder in sorted(
            [p for p in scratch.rglob("*") if p.is_dir()] + [scratch],
            key=lambda p: len(p.parts),
            reverse=True,
        ):
            fd = os.open(folder, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            try:
                os.fsync(fd)
            finally:
                os.close(fd)
        with ProjectStore(parent)._directory(()) as fd:
            # Reserve without overwrite, then replace only that empty owned directory.
            os.mkdir(name, mode=0o700, dir_fd=fd)
            reserved = True
            os.replace(scratch.name, name, src_dir_fd=fd, dst_dir_fd=fd)
            reserved = False
            os.fsync(fd)
    finally:
        if reserved:
            target.rmdir()
        if scratch.exists():
            shutil.rmtree(scratch)


class BackupService:
    def __init__(self, assets):
        self.assets, self.store = assets, assets.store

    def export(self, destination):
        with self.store.exclusive_lock(".tabi-worker.lock"), self.store.writer_lock():
            if any(j.state in {"queued", "running"} for j in JobLedger(self.store).all()):
                raise StorageError("Pause or finish queued/running jobs before backing up")
            original_paths = tree_files(self.store)
            # These mappings never change an asset/snapshot or grant access outside the copy.
            inputs = {p: (self.store, p, None) for p in original_paths if p != ROOTS_FILE}
            roots, warnings = set(), []
            assets = self.assets.list_assets()
            for asset in assets:
                self.assets.require_valid(AssetRef(id=asset.id, version=asset.version))
            documents = [
                *assets,
                *AuthoringService(self.assets).documents("releases", ReleaseRecord),
            ]
            mandatory = {
                (f.location.root_id, f.location.path): (f.sha256, f.size_bytes)
                for a in assets
                for f in [*a.files, *a.proxies]
            }
            refs = {(p.root_id, p.path): p for doc in documents for p in references(doc)}
            for key, ref in sorted(refs.items()):
                source = (
                    self.store
                    if ref.root_id == "project"
                    else (
                        ProjectStore(self.assets.roots[ref.root_id])
                        if ref.root_id in self.assets.roots
                        else None
                    )
                )
                try:
                    if source is None:
                        raise FileNotFoundError("original root is not registered")
                    parts = source._parts(ref.path)
                    with source._directory(parts[:-1]) as directory:
                        mode = os.stat(parts[-1], dir_fd=directory, follow_symlinks=False).st_mode
                    if stat.S_ISDIR(mode) and key not in mandatory:
                        paths = tree_files(source, ref.path, exclude=False)
                        if not paths:
                            warnings.append(
                                f"Empty historical source folder: {ref.root_id}/{ref.path}"
                            )
                            continue
                    else:
                        with source_file(source, ref.path):
                            pass
                        paths = [ref.path]
                except (FileNotFoundError, NotADirectoryError):
                    if key in mandatory:
                        raise StorageError(
                            f"Required media is missing: {ref.root_id}/{ref.path}"
                        ) from None
                    warnings.append(
                        f"Historical source/evidence unavailable: {ref.root_id}/{ref.path}"
                    )
                    continue
                if ref.root_id != "project":
                    roots.add(ref.root_id)
                for path in paths:
                    target = (
                        path
                        if ref.root_id == "project"
                        else f".portable-media/{ref.root_id}/{path}"
                    )
                    inputs[target] = (source, path, mandatory.get((ref.root_id, path)))
            # Keep embedded roots from a previous restore even when only historical files use them.
            try:
                roots.update(
                    PortableRoots.model_validate_json(self.store._read_bytes(ROOTS_FILE)).roots
                )
            except FileNotFoundError:
                pass
            estimated = sum((s.root / p).stat().st_size for s, p, _ in inputs.values())
            if shutil.disk_usage(Path(destination).parent).free < estimated + 256 * 1024**2:
                raise StorageError("Insufficient destination space for an independent backup copy")
            with publication(destination, outside=self.store.root) as stage:
                files = []
                for target, (source, path, expected) in sorted(inputs.items()):
                    digest, size = transfer(source, path, stage / "project" / target, expected)
                    files.append(
                        HashedFile(
                            location=MediaPath(path=f"project/{target}"),
                            sha256=digest,
                            size_bytes=size,
                        )
                    )
                copied = ProjectStore(stage / "project")
                mapping = PortableRoots(schema_version="1.0", roots=sorted(roots))
                copied._atomic_write(ROOTS_FILE, canonical_bytes(mapping), overwrite=False)
                digest, size = transfer(copied, ROOTS_FILE)
                files.append(
                    HashedFile(
                        location=MediaPath(path=f"project/{ROOTS_FILE}"),
                        sha256=digest,
                        size_bytes=size,
                    )
                )
                # Detect a concurrent renderer or outside editor; never clean up source media.
                if tree_files(self.store) != original_paths:
                    raise StorageError("Project files changed during backup; retry when idle")
                for record in files:
                    path = record.location.path.removeprefix("project/")
                    transfer(copied, path, expected=(record.sha256, record.size_bytes))
                    if path in inputs:
                        source, relative, _ = inputs[path]
                        transfer(source, relative, expected=(record.sha256, record.size_bytes))
                check_project(copied, self.store.read().id)
                manifest = BackupManifest(
                    schema_version="1.0",
                    project_id=self.store.read().id,
                    created_at=datetime.now(UTC),
                    files=files,
                    total_bytes=sum(f.size_bytes for f in files),
                    warnings=warnings,
                )
                ProjectStore(stage)._atomic_write(
                    "manifest.json", canonical_bytes(manifest), overwrite=False
                )
            return manifest

    @staticmethod
    def inspect(source):
        store = ProjectStore(source)
        manifest = store.read("manifest.json")
        if not isinstance(manifest, BackupManifest):
            raise StorageError("select a Tabi private backup folder")
        actual = tree_files(store, "project", exclude=False)
        if set(actual) != {f.location.path for f in manifest.files}:
            raise StorageError("backup inventory differs from its manifest")
        for record in manifest.files:
            transfer(store, record.location.path, expected=(record.sha256, record.size_bytes))
        check_project(ProjectStore(store.root / "project"), manifest.project_id)
        return manifest

    @staticmethod
    def restore(source, destination):
        source = ProjectStore(source)
        manifest = BackupService.inspect(source.root)
        if shutil.disk_usage(Path(destination).parent).free < manifest.total_bytes + 256 * 1024**2:
            raise StorageError("Insufficient destination space to restore the private backup")
        with publication(destination, outside=source.root) as stage:
            for record in manifest.files:
                transfer(
                    source,
                    record.location.path,
                    stage / record.location.path.removeprefix("project/"),
                    (record.sha256, record.size_bytes),
                )
                transfer(
                    ProjectStore(stage),
                    record.location.path.removeprefix("project/"),
                    expected=(record.sha256, record.size_bytes),
                )
            check_project(ProjectStore(stage), manifest.project_id)
        return manifest
