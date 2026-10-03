import json
from pathlib import Path

import pytest

from tabi.cli.main import main
from tabi.core.assets import AssetService
from tabi.core.config import load_settings
from tabi.core.episodes import EpisodeService
from tabi.core.fixtures import generate_fixtures
from tabi.core.models import Episode
from tabi.core.persistence import ImmutableDocument, ProjectStore, StorageError
from tabi.core.render.backend import FrozenRegistry


@pytest.fixture
def setup(tmp_path):
    root = tmp_path / "Snapshot's 東京 project"
    generate_fixtures(root)
    store = ProjectStore(root)
    settings = load_settings(None, env={}, cwd=tmp_path, home=Path.home())
    service = EpisodeService(AssetService(store), settings)
    return service, store.read("episodes/episode.synthetic.json")


def test_compile_idempotence_edits_and_snapshot_export_preserve_frozen_bytes(setup, tmp_path):
    service, episode = setup
    output = tmp_path / "Frozen 日本語.json"
    first = service.compile(episode, purpose="synthetic_test", output=output)
    before = Path(first.snapshot_path).read_bytes()
    assert output.read_bytes() == before
    assert first == service.compile(episode, purpose="synthetic_test")
    edited = episode.model_copy(update={"title": "New draft", "seed": episode.seed + 1})
    service.store.save_draft(edited, expected_revision=episode.revision)
    second = service.compile(edited, purpose="synthetic_test")
    assert first.snapshot_sha256 != second.snapshot_sha256
    assert Path(first.snapshot_path).read_bytes() == before
    FrozenRegistry(service.assets, service.store.read_snapshot(first.snapshot_sha256))
    assert (
        service.inspect_snapshot(first.snapshot_sha256)["snapshot"]["episode"]["title"]
        == episode.title
    )
    with pytest.raises(StorageError, match="exists"):
        service.compile(edited, purpose="synthetic_test", output=output)
    assert output.read_bytes() == before


def test_compile_validation_is_read_only_and_reports_missing_media(setup):
    service, episode = setup
    before = {str(p): p.read_bytes() for p in service.store.root.rglob("*.json")}
    report = service.validate(episode, purpose="synthetic_test")
    assert report.valid and report.scope == "compile"
    assert {str(p): p.read_bytes() for p in service.store.root.rglob("*.json")} == before
    (service.store.root / "assets/fixture.idle/000000.png").unlink()
    failed = service.validate(episode, purpose="synthetic_test")
    assert not failed.valid and failed.scope == "compile"
    assert failed.issues[0].code == "compile_failed" and failed.issues[0].suggested_fix
    assert "fixture.idle" in failed.issues[0].message


def test_synthetic_review_and_tampered_snapshot_are_rejected(setup, tmp_path):
    service, episode = setup
    result = service.compile(episode, purpose="synthetic_test")
    with pytest.raises(StorageError, match="fixtures"):
        service.review_snapshot(
            result.snapshot_sha256,
            expected_hash=result.review_content_sha256,
            reviewer="Test",
            note="Cannot approve synthetic",
        )
    path = Path(result.snapshot_path)
    raw = json.loads(path.read_bytes())
    raw["episode"]["title"] = "Tampered"
    path.write_text(json.dumps(raw))
    with pytest.raises(ImmutableDocument):
        service.frame(result.snapshot_sha256, 0, tmp_path / "no.png")
    assert not (tmp_path / "no.png").exists()


def test_cli_validation_compile_snapshot_show_and_invalid_frame(setup, tmp_path, capsys):
    service, episode = setup
    path = service.store.root / "episodes/episode.synthetic.json"
    args = [str(path), "--project", str(service.store.root), "--purpose", "synthetic_test"]
    assert main(["validate", *args]) == 0
    assert json.loads(capsys.readouterr().out)["scope"] == "compile"
    assert main(["compile", *args]) == 0
    result = json.loads(capsys.readouterr().out)
    digest = result["snapshot_sha256"]
    assert main(["snapshot", "show", digest, "--project", str(service.store.root)]) == 0
    assert json.loads(capsys.readouterr().out)["result"] == result
    output = tmp_path / "no.png"
    assert (
        main(
            [
                "frame",
                digest,
                "--project",
                str(service.store.root),
                "--frame",
                "300",
                "--output",
                str(output),
            ]
        )
        == 4
    )
    assert not output.exists()


def test_production_validation_reports_approval_requirement(setup):
    service, episode = setup
    result = service.validate(Episode.model_validate(episode), purpose="production")
    assert not result.valid and "approval" in result.issues[0].message
