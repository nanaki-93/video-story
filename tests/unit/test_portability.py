from datetime import UTC, datetime

import pytest

from tabi.core.assets import AssetService
from tabi.core.fixtures import generate_fixtures
from tabi.core.models import Asset, CompiledSnapshot
from tabi.core.models.base import AssetRef, MediaPath, canonical_bytes
from tabi.core.persistence import ProjectBusy, ProjectStore, StorageError
from tabi.core.portability import BackupService
from tabi.core.timeline.compiler import ActionCompiler


def project(tmp_path):
    root = tmp_path / "Private 東京 project"
    generate_fixtures(root)
    store = ProjectStore(root)
    assets = AssetService(store)
    snapshot = ActionCompiler(assets, purpose="preview").compile(
        store.read("episodes/episode.synthetic.json")
    )
    store.save_snapshot(snapshot)
    (root / "private-notes.txt").write_text("PRIVATE rights notes — not a public bundle")
    return assets


def test_backup_restores_external_media_edits_and_exact_reviewed_documents(tmp_path, snapshot_data):
    assets = project(tmp_path)
    external = tmp_path / "Originals"
    external.mkdir()
    asset = next(a for a in assets.list_assets() if a.kind == "audio")
    data = assets.resolve(asset.files[0].location).read_bytes()
    (external / "master 東京.wav").write_bytes(data)
    ref = MediaPath(root_id="masters", path="master 東京.wav")
    changed = Asset.model_validate(
        {
            **asset.model_dump(),
            "source": ref,
            "files": [{**asset.files[0].model_dump(), "location": ref}],
        }
    )
    assets.store.save_draft(changed, expected_revision=asset.revision)
    assets = AssetService(assets.store, roots={"masters": external})
    # Contract-only review fixture; this does not approve synthetic art for publication.
    raw = CompiledSnapshot.model_validate({**snapshot_data, "purpose": "production"})
    reviewed = CompiledSnapshot.model_validate(
        {
            **raw.model_dump(),
            "approval": {
                "status": "approved",
                "content_sha256": raw.approval_hash,
                "reviewer": "Isolated persistence test",
                "reviewed_at": datetime.now(UTC),
            },
        }
    )
    digest = assets.store.save_snapshot(reviewed)
    snapshots = {p.name: p.read_bytes() for p in (assets.store.root / "snapshots").glob("*.json")}
    original = assets.store._read_bytes(f"registry/assets/{asset.id}/{asset.version}.json")
    backup = tmp_path / "Private backup 東京"
    manifest = BackupService(assets).export(backup)
    assert not manifest.warnings
    assert (backup / "project/private-notes.txt").read_text().startswith("PRIVATE")
    # Disconnect the external source and prove no caller-provided root is needed.
    (external / ref.path).unlink()
    restored = tmp_path / "Restored project"
    assert BackupService.restore(backup, restored) == manifest
    service = AssetService(ProjectStore(restored))
    source = service.require_valid(AssetRef(id=asset.id, version=asset.version))
    assert service.resolve(source.files[0].location).read_bytes() == data
    assert service.store._read_bytes(f"registry/assets/{asset.id}/{asset.version}.json") == original
    assert service.store.read_snapshot(digest).approval == reviewed.approval
    assert all(
        (restored / "snapshots" / name).read_bytes() == value for name, value in snapshots.items()
    )
    assert service.store._read_bytes("episodes/episode.synthetic.json") == assets.store._read_bytes(
        "episodes/episode.synthetic.json"
    )
    # An already portable project can be backed up again without changing identities.
    assert not BackupService(service).export(tmp_path / "Second backup").warnings
    with pytest.raises(StorageError, match="exists"):
        BackupService.restore(backup, restored)


def test_backup_rejects_symlinks_corruption_unsafe_paths_and_busy_workers(tmp_path):
    assets = project(tmp_path)
    with assets.store.exclusive_lock(".tabi-worker.lock"), pytest.raises(ProjectBusy):
        BackupService(assets).export(tmp_path / "busy")
    assert not (tmp_path / "busy").exists()
    link = assets.store.root / "alias"
    link.symlink_to(assets.store.root / "private-notes.txt")
    with pytest.raises(StorageError, match="symlink"):
        BackupService(assets).export(tmp_path / "bad-link")
    link.unlink()
    with pytest.raises(StorageError, match="outside"):
        BackupService(assets).export(assets.store.root / "recursive")
    backup = tmp_path / "good"
    manifest = BackupService(assets).export(backup)
    (backup / "project/private-notes.txt").write_text("corrupted")
    with pytest.raises(StorageError, match="hash"):
        BackupService.restore(backup, tmp_path / "must-not-exist")
    assert not (tmp_path / "must-not-exist").exists()
    raw = manifest.model_dump(mode="json")
    raw["files"][0]["location"]["path"] = "project/../../escape"
    (backup / "manifest.json").write_bytes(canonical_bytes(raw))
    with pytest.raises(ValueError):
        BackupService.restore(backup, tmp_path / "must-not-exist")
    assert not list(tmp_path.glob(".tabi-portable-*"))


def test_concurrent_source_edit_leaves_no_partial_backup(tmp_path, monkeypatch):
    assets = project(tmp_path)
    import tabi.core.portability as module

    original = module.transfer

    def mutate(store, relative, output=None, expected=None):
        result = original(store, relative, output, expected)
        if relative == "private-notes.txt" and output:
            (store.root / relative).write_text("Edited concurrently")
        return result

    monkeypatch.setattr(module, "transfer", mutate)
    with pytest.raises(StorageError, match="hash"):
        BackupService(assets).export(tmp_path / "race")
    assert not (tmp_path / "race").exists()
    assert (assets.store.root / "private-notes.txt").read_text() == "Edited concurrently"
    assert not list(tmp_path.glob(".tabi-portable-*"))


def test_private_evidence_folders_copy_and_missing_historical_sources_are_reported(tmp_path):
    assets = project(tmp_path)
    evidence = tmp_path / "Evidence"
    (evidence / "Source package").mkdir(parents=True)
    (evidence / "Source package/notes.txt").write_text("Private test evidence")
    asset = assets.list_assets()[0]
    changed = Asset.model_validate(
        {
            **asset.model_dump(),
            "source": {"root_id": "disconnected", "path": "old-original.png"},
            "provenance": {
                **asset.provenance.model_dump(),
                "licence_evidence": [{"root_id": "evidence", "path": "Source package"}],
            },
        }
    )
    assets.store.save_draft(changed, expected_revision=asset.revision)
    assets = AssetService(assets.store, roots={"evidence": evidence})
    backup = tmp_path / "With evidence"
    manifest = BackupService(assets).export(backup)
    assert len(manifest.warnings) == 1 and "disconnected/old-original.png" in manifest.warnings[0]
    assert (
        backup / "project/.portable-media/evidence/Source package/notes.txt"
    ).read_text() == "Private test evidence"
    BackupService.restore(backup, tmp_path / "Restored evidence")
