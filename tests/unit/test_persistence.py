import copy
import errno
import json
import multiprocessing
import os
from pathlib import Path
from typing import Literal

import pytest

from tabi.core.documents import DocumentError, validate_data
from tabi.core.models import Project
from tabi.core.models.base import MediaPath, canonical_bytes
from tabi.core.persistence import (
    ImmutableDocument,
    MigrationRegistry,
    ProjectBusy,
    ProjectStore,
    RevisionConflict,
    StorageError,
    UnsafePath,
    document_path,
    resolve_media_path,
)


class FutureProject(Project):
    """Synthetic minor version used only to exercise the migration infrastructure."""

    schema_version: Literal["1.1"]
    description: str


def upgraded(data):
    return {**data, "schema_version": "1.1", "description": "Synthetic migration test"}


@pytest.fixture
def store(tmp_path):
    return ProjectStore.initialize(tmp_path / "Marco's 東京 project", "Synthetic persistence test")


def test_atomic_save_reopen_revision_and_exact_backup(store):
    project = store.read()
    original = (store.root / "project.json").read_bytes()
    changed = project.model_copy(update={"title": "Updated 日本語 title"})
    saved = store.save_draft(changed, expected_revision=0)
    assert saved.revision == 1
    assert ProjectStore(store.root).read() == saved
    assert saved.created_at == project.created_at
    backups = list((store.root / ".backups").rglob("*.bak"))
    assert len(backups) == 1 and backups[0].read_bytes() == original
    assert not list(store.root.rglob("*.tmp"))


def test_stale_writer_cannot_overwrite_newer_document(store):
    first = store.read()
    stale = ProjectStore(store.root).read()
    saved = store.save_draft(
        first.model_copy(update={"title": "First editor"}), expected_revision=0
    )
    with pytest.raises(RevisionConflict):
        store.save_draft(stale.model_copy(update={"title": "Stale editor"}), expected_revision=0)
    assert store.read() == saved


def test_create_draft_is_no_clobber_and_reopens(store, episode_data):
    episode = validate_data(episode_data)
    saved = store.save_draft(episode, expected_revision=None)
    assert store.read(document_path(episode)) == saved
    with pytest.raises(RevisionConflict):
        store.save_draft(episode, expected_revision=None)
    with pytest.raises(RevisionConflict):
        store.save_draft(episode, expected_revision=True)


def test_revalidates_mutable_nested_collections_before_writing(store, episode_data):
    episode = validate_data(episode_data)
    episode.scenes.clear()
    with pytest.raises(DocumentError):
        store.save_draft(episode, expected_revision=None)
    assert not (store.root / "episodes" / f"{episode.id}.json").exists()


def test_replace_failure_preserves_old_document_and_backup(store, monkeypatch):
    original = (store.root / "project.json").read_bytes()
    project = store.read()

    def fail_replace(*args, **kwargs):
        raise OSError(errno.ENOSPC, "synthetic disk-full failure")

    monkeypatch.setattr(os, "replace", fail_replace)
    with pytest.raises(OSError, match="disk-full"):
        store.save_draft(project.model_copy(update={"title": "Not committed"}), expected_revision=0)
    assert (store.root / "project.json").read_bytes() == original
    assert all(p.read_bytes() == original for p in (store.root / ".backups").rglob("*.bak"))
    assert not list(store.root.rglob("*.tmp"))


def test_flush_failure_preserves_source(store, monkeypatch):
    original = (store.root / "project.json").read_bytes()
    project = store.read()

    def fail_sync(*args):
        raise OSError(errno.EIO, "synthetic flush failure")

    monkeypatch.setattr(os, "fsync", fail_sync)
    with pytest.raises(OSError, match="flush failure"):
        store.save_draft(project, expected_revision=0)
    assert (store.root / "project.json").read_bytes() == original
    assert not list(store.root.rglob("*.tmp"))


def test_corrupt_temporary_bytes_never_replace_source(store, monkeypatch):
    original = (store.root / "project.json").read_bytes()
    read_at = store._read_at

    def damaged(directory, name):
        data = read_at(directory, name)
        return data[:-1] if name.endswith(".tmp") else data

    monkeypatch.setattr(store, "_read_at", damaged)
    with pytest.raises(StorageError, match="verification"):
        store.save_draft(store.read(), expected_revision=0)
    assert (store.root / "project.json").read_bytes() == original


def _hold_lock(root, ready):
    with ProjectStore(Path(root)).writer_lock():
        ready.send("locked")
        ready.recv()


def test_cross_process_writer_lock_and_crash_recovery(store):
    context = multiprocessing.get_context("spawn")
    parent, child = context.Pipe()
    process = context.Process(target=_hold_lock, args=(str(store.root), child))
    process.start()
    try:
        assert parent.poll(10)
        assert parent.recv() == "locked"
        with pytest.raises(ProjectBusy):
            store.save_draft(store.read(), expected_revision=0)
        # Terminate only this test-owned child; kernel must release its flock.
        process.terminate()
        process.join(10)
        assert not process.is_alive()
        assert store.save_draft(store.read(), expected_revision=0).revision == 1
    finally:
        if process.is_alive():
            process.terminate()
        process.join(10)
        parent.close()
        child.close()


def _pause_before_replace(root, ready):
    store = ProjectStore(Path(root))

    def pause(*args, **kwargs):
        ready.send("ready to replace")
        ready.recv()

    os.replace = pause
    store.save_draft(store.read().model_copy(update={"title": "Interrupted"}), expected_revision=0)


def test_process_exit_before_publication_keeps_source_and_backup(store):
    original = (store.root / "project.json").read_bytes()
    context = multiprocessing.get_context("spawn")
    parent, child = context.Pipe()
    process = context.Process(target=_pause_before_replace, args=(str(store.root), child))
    process.start()
    try:
        assert parent.poll(10)
        assert parent.recv() == "ready to replace"
        process.terminate()
        process.join(10)
        assert not process.is_alive()
        assert (store.root / "project.json").read_bytes() == original
        assert [p.read_bytes() for p in (store.root / ".backups").rglob("*.bak")] == [original]
        # Abrupt exit can leave a temp file; it never becomes the canonical document.
        assert list(store.root.glob(".project.json.*.tmp"))
        reopened = ProjectStore(store.root)
        assert reopened.read().title != "Interrupted"
        assert reopened.save_draft(reopened.read(), expected_revision=0).revision == 1
    finally:
        if process.is_alive():
            process.terminate()
        process.join(10)
        parent.close()
        child.close()


def test_snapshot_is_idempotent_immutable_and_tamper_checked(store, snapshot_data):
    snapshot = validate_data(snapshot_data)
    digest = store.save_snapshot(snapshot)
    path = store.root / "snapshots" / f"{digest}.json"
    before = path.stat().st_mtime_ns
    assert store.save_snapshot(snapshot) == digest
    assert path.stat().st_mtime_ns == before
    assert store.read(f"snapshots/{digest}.json") == snapshot
    with pytest.raises(ImmutableDocument):
        store.save_draft(snapshot, expected_revision=0)
    altered = copy.deepcopy(snapshot_data)
    altered["episode"]["title"] = "Changed synthetic title"
    new_digest = store.save_snapshot(validate_data(altered))
    assert new_digest != digest and path.read_bytes() == canonical_bytes(snapshot)
    path.write_bytes(b"corruption injected by test")
    with pytest.raises(ImmutableDocument):
        store.read_snapshot(digest)
    with pytest.raises(ImmutableDocument):
        store.save_snapshot(snapshot)
    assert path.read_bytes() == b"corruption injected by test"


def test_approved_version_requires_new_version(store):
    raw = json.loads(
        (Path(__file__).resolve().parents[2] / "examples/scene.train.json").read_text()
    )
    raw["approval"] = {
        "status": "approved",
        "content_sha256": validate_data(raw).approval_hash,
        "reviewer": "Synthetic guard test",
        "reviewed_at": "2026-10-03T00:00:00Z",
    }
    approved = validate_data(raw)
    store.save_draft(approved, expected_revision=None)
    original = (store.root / document_path(approved)).read_bytes()
    raw["approval"] = {"status": "draft"}
    draft = validate_data(raw)
    with pytest.raises(ImmutableDocument):
        store.save_draft(draft, expected_revision=0)
    assert (store.root / document_path(approved)).read_bytes() == original
    migrations = MigrationRegistry()
    migrations.register("1.0", "1.1", upgraded)
    with pytest.raises(ImmutableDocument):
        store.migrate(
            document_path(approved),
            expected_revision=0,
            target_version="1.1",
            target_model=FutureProject,
            migrations=migrations,
        )
    assert (store.root / document_path(approved)).read_bytes() == original
    assert not (store.root / ".backups").exists()
    raw["version"] = "1.1"
    store.save_draft(validate_data(raw), expected_revision=None)


def test_symlinked_metadata_and_traversal_cannot_escape(store, tmp_path, episode_data):
    outside = tmp_path / "outside"
    outside.mkdir()
    (store.root / "episodes").rmdir()
    (store.root / "episodes").symlink_to(outside, target_is_directory=True)
    with pytest.raises(UnsafePath):
        store.save_draft(validate_data(episode_data), expected_revision=None)
    assert list(outside.iterdir()) == []
    with pytest.raises(UnsafePath):
        store.read("../outside/project.json")
    with pytest.raises(UnsafePath):
        store.read_snapshot("../project")


def test_symlinked_document_and_backup_folder_preserve_targets(store, tmp_path):
    project = store.read()
    victim = tmp_path / "must survive.json"
    victim.write_bytes(canonical_bytes(project))
    path = store.root / "project.json"
    path.unlink()
    path.symlink_to(victim)
    with pytest.raises(UnsafePath):
        store.save_draft(project, expected_revision=0)
    assert victim.read_bytes() == canonical_bytes(project)
    path.unlink()
    path.write_bytes(canonical_bytes(project))
    (store.root / ".backups").symlink_to(tmp_path, target_is_directory=True)
    with pytest.raises(UnsafePath):
        store.save_draft(project, expected_revision=0)
    assert path.read_bytes() == canonical_bytes(project)


def test_media_resolution_uses_only_authorized_roots(store, tmp_path):
    outside = tmp_path / "external 音楽"
    outside.mkdir()
    ref = MediaPath(root_id="music", path="Marco's song.wav")
    with pytest.raises(UnsafePath):
        resolve_media_path(ref, store.root, {})
    assert resolve_media_path(ref, store.root, {"music": outside}) == outside / ref.path
    (store.root / "assets" / "escape").symlink_to(outside, target_is_directory=True)
    with pytest.raises(UnsafePath):
        resolve_media_path(MediaPath(path="assets/escape/song.wav"), store.root, {})


def test_init_preserves_occupied_directory_and_validates_before_writes(tmp_path):
    directory = tmp_path / "existing"
    directory.mkdir()
    original = directory / "art.png"
    original.write_bytes(b"synthetic existing source")
    with pytest.raises(StorageError):
        ProjectStore.initialize(directory, "Test")
    assert sorted(p.name for p in directory.iterdir()) == ["art.png"]
    with pytest.raises(DocumentError):
        ProjectStore.initialize(tmp_path / "invalid", "  ")
    assert not (tmp_path / "invalid").exists()


def test_successful_migration_keeps_exact_original_backup(store):
    original = (store.root / "project.json").read_bytes()
    migrations = MigrationRegistry()
    migrations.register("1.0", "1.1", upgraded)
    updated = store.migrate(
        "project.json",
        expected_revision=0,
        target_version="1.1",
        target_model=FutureProject,
        migrations=migrations,
    )
    assert updated.revision == 1 and updated.schema_version == "1.1"
    assert FutureProject.model_validate_json((store.root / "project.json").read_bytes()) == updated
    assert [p.read_bytes() for p in (store.root / ".backups").rglob("*.bak")] == [original]


@pytest.mark.parametrize("failure", ["transform", "validation", "identity", "rename"])
def test_failed_migration_preserves_original_and_backup(store, monkeypatch, failure):
    original = (store.root / "project.json").read_bytes()

    def transform(data):
        assert any((store.root / ".backups").rglob("*.bak"))
        if failure == "transform":
            raise RuntimeError("synthetic interrupted migration")
        migrated = upgraded(data)
        if failure == "validation":
            migrated["unexpected"] = True
        if failure == "identity":
            migrated["id"] = "changed-id"
        return migrated

    def fail_replace(*args, **kwargs):
        raise OSError("synthetic migration rename failure")

    if failure == "rename":
        monkeypatch.setattr(os, "replace", fail_replace)
    migrations = MigrationRegistry()
    migrations.register("1.0", "1.1", transform)
    with pytest.raises((RuntimeError, DocumentError, StorageError, OSError)):
        store.migrate(
            "project.json",
            expected_revision=0,
            target_version="1.1",
            target_model=FutureProject,
            migrations=migrations,
        )
    assert (store.root / "project.json").read_bytes() == original
    assert [p.read_bytes() for p in (store.root / ".backups").rglob("*.bak")] == [original]
    assert not list(store.root.rglob("*.tmp"))


def test_migration_never_rewrites_snapshots_and_rejects_major_or_stale_versions(
    store, snapshot_data
):
    digest = store.save_snapshot(validate_data(snapshot_data))
    migrations = MigrationRegistry()
    migrations.register("1.0", "1.1", upgraded)
    with pytest.raises(ImmutableDocument):
        store.migrate(
            f"snapshots/{digest}.json",
            expected_revision=0,
            target_version="1.1",
            target_model=FutureProject,
            migrations=migrations,
        )
    assert store.read_snapshot(digest)
    with pytest.raises(StorageError):
        migrations.register("1.1", "2.0", upgraded)
    with pytest.raises(RevisionConflict):
        store.migrate(
            "project.json",
            expected_revision=7,
            target_version="1.1",
            target_model=FutureProject,
            migrations=migrations,
        )
