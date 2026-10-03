import json
import os
import subprocess
import sys

import yaml

from tabi.core.fixtures import generate_fixtures
from tabi.core.persistence import ProjectStore


def invoke(tmp_path, *args, expected=0):
    env = {key: value for key, value in os.environ.items() if not key.startswith("TABI_")}
    env.update(XDG_CONFIG_HOME=str(tmp_path / "config"), TABI_CACHE_ROOT=str(tmp_path / "cache"))
    result = subprocess.run(
        [sys.executable, "-m", "tabi", *map(str, args)],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == expected, result.stderr + result.stdout
    assert "Traceback" not in result.stderr
    return json.loads(result.stdout) if result.stdout else None


def request(tmp_path, data, name="request.json"):
    path = tmp_path / name
    path.write_text(yaml.safe_dump(data) if path.suffix == ".yaml" else json.dumps(data))
    return path


def test_cli_creates_still_episode_edits_and_preserves_stale_or_invalid_requests(
    tmp_path, review_project
):
    author, _, _, _ = review_project
    project = author.store.root
    template = invoke(
        tmp_path,
        "author",
        "still-template",
        "--project",
        project,
        request(
            tmp_path,
            {
                "asset": {"id": "test-background", "version": "1.0"},
                "id": "still-test",
            },
            "still.yaml",
        ),
    )
    assert template["approval"]["status"] == "draft"
    created = invoke(
        tmp_path,
        "author",
        "create-episode",
        "--project",
        project,
        request(
            tmp_path,
            {
                "id": "new-episode",
                "title": "A quiet 東京 scene",
                "fps": {"num": 30000, "den": 1001},
                "canvas": {"width": 64, "height": 36},
                "duration_frames": 37,
                "template": {"id": "still-test", "version": "1.0"},
            },
        ),
    )
    assert created["duration_frames"] == 37 and created["revision"] == 0
    edit = request(
        tmp_path, {"expected_revision": 0, "command": {"kind": "title", "title": "Edited title"}}
    )
    result = invoke(tmp_path, "author", "edit", "new-episode", edit, "--project", project)
    assert result["title"] == "Edited title" and result["revision"] == 1
    invoke(tmp_path, "author", "edit", "new-episode", edit, "--project", project, expected=4)
    bad = request(
        tmp_path,
        {"expected_revision": 1, "command": {"kind": "title", "title": "Wrong", "extra": True}},
    )
    invoke(tmp_path, "author", "edit", "new-episode", bad, "--project", project, expected=4)
    bad.write_text("expected_revision: 1\nexpected_revision: 0\n")
    bad = bad.rename(tmp_path / "duplicate.yaml")
    invoke(tmp_path, "author", "edit", "new-episode", bad, "--project", project, expected=4)
    assert invoke(tmp_path, "author", "show", "new-episode", "--project", project) == result
    lanes = invoke(tmp_path, "author", "lanes", "new-episode", "--project", project)
    assert lanes[0]["items"][0]["end_frame"] == 37
    catalog = invoke(tmp_path, "author", "catalog", "--project", project)
    assert len(catalog["episodes"]) == 2 and len(catalog["templates"]) == 2


def test_cli_install_versions_and_metadata_review_share_guards(tmp_path, review_project):
    author, template, pack, _ = review_project
    project = author.store.root
    for asset in author.assets.list_assets():
        invoke(
            tmp_path,
            "asset",
            "approve",
            project,
            asset.id,
            asset.version,
            "--reviewed-hash",
            asset.approval_hash,
            "--reviewer",
            "Automated test only",
            "--note",
            "Temporary owned test geometry; no real artwork approval",
        )
    for doc in (template, pack):
        shown = invoke(
            tmp_path,
            "author",
            "metadata",
            doc.document_type,
            doc.id,
            doc.version,
            "--project",
            project,
        )
        assert shown["review_content_sha256"] == doc.approval_hash
        args = [
            "author",
            "review",
            doc.document_type,
            doc.id,
            doc.version,
            "--project",
            project,
            "--reviewer",
            "Automated test only",
            "--note",
            "Guard test only",
        ]
        invoke(tmp_path, *args, "--reviewed-hash", "0" * 64, expected=4)
        approved = invoke(tmp_path, *args, "--reviewed-hash", doc.approval_hash)
        assert approved["approval"]["status"] == "approved"
    metadata = {**approved, "version": "1.1", "revision": 0}
    path = request(tmp_path, metadata)
    invoke(tmp_path, "author", "install", path, "--project", project, expected=4)
    metadata["approval"] = {"status": "draft"}
    draft = invoke(tmp_path, "author", "install", request(tmp_path, metadata), "--project", project)
    assert draft["version"] == "1.1" and draft["approval"]["status"] == "draft"
    asset = author.assets.list_assets()[0]
    version = invoke(
        tmp_path,
        "author",
        "asset-version",
        asset.id,
        asset.version,
        request(
            tmp_path,
            {
                "version": "1.1",
                "provenance": asset.provenance.model_dump(mode="json"),
                "compatibility": asset.compatibility.model_dump(mode="json"),
            },
        ),
        "--project",
        project,
    )
    assert version["approval"]["status"] == "draft"
    assert (
        author.assets.load({"id": asset.id, "version": asset.version}).approval.status == "approved"
    )


def test_cli_audio_proposal_and_apply_preserve_visuals_and_reject_conflicts(tmp_path):
    project = tmp_path / "Audio 東京"
    generate_fixtures(project)
    store = ProjectStore(project)
    original = store.read("episodes/episode.synthetic.json")
    track = {
        **original.tracks[0].model_dump(mode="json"),
        "trim_end_sample": 24000,
        "gain_db": -12.0,
    }
    path = request(tmp_path, {"expected_revision": 0, "tracks": [track]})
    proposal = invoke(tmp_path, "audio", "propose", original.id, path, "--project", project)
    assert proposal["can_apply"] and proposal["effective_end_sample"] == 24000
    assert store.read("episodes/episode.synthetic.json").revision == 0
    saved = invoke(tmp_path, "audio", "edit", original.id, path, "--project", project)
    assert saved["revision"] == 1 and saved["scenes"] == original.model_dump(mode="json")["scenes"]
    invoke(tmp_path, "audio", "edit", original.id, path, "--project", project, expected=4)
    request(tmp_path, {"expected_revision": 1, "tracks": [{**track, "start_sample": 480000}]})
    denied = invoke(
        tmp_path, "audio", "propose", original.id, path, "--project", project, expected=2
    )
    assert not denied["can_apply"] and denied["issues"]
    invoke(tmp_path, "audio", "edit", original.id, path, "--project", project, expected=4)
    assert store.read("episodes/episode.synthetic.json").model_dump(mode="json") == saved


def test_cli_preferences_and_tools_compare_before_saving_and_keep_backups(tmp_path):
    shown = invoke(tmp_path, "preferences", "show")
    assert not shown["preferences_saved"] and shown["config_sha256"] is None
    value = {**shown["preferences"], "theme": "contrast"}
    path = request(tmp_path, {"preferences": value, "expected_revision": None})
    saved = invoke(tmp_path, "preferences", "save", path)
    invoke(tmp_path, "preferences", "save", path, expected=4)
    value = {**saved, "export_preset": "proxy"}
    request(tmp_path, {"preferences": value, "expected_revision": saved["revision"]})
    updated = invoke(tmp_path, "preferences", "save", path)
    assert updated["revision"] == 1 and updated["theme"] == "contrast"
    invoke(tmp_path, "preferences", "save", path, expected=4)
    tools = {"ffmpeg": "/test/ffmpeg", "ffprobe": "/test/ffprobe", "expected_hash": None}
    first = invoke(tmp_path, "preferences", "tools", request(tmp_path, tools))
    assert first["restart_required"] and len(first["config_sha256"]) == 64
    invoke(tmp_path, "preferences", "tools", path, expected=4)
    second = invoke(
        tmp_path,
        "preferences",
        "tools",
        request(
            tmp_path,
            {
                **tools,
                "ffmpeg": "/test/new ffmpeg",
                "expected_hash": first["config_sha256"],
            },
        ),
    )
    assert first["config_sha256"] != second["config_sha256"]
    actual = invoke(tmp_path, "preferences", "show")
    assert actual["ffmpeg"] == "/test/new ffmpeg" and actual["preferences"] == updated
    assert list((tmp_path / "config/tabi/.backups").rglob("*.bak"))


def test_cli_import_accepts_safe_yaml_and_bounds_request_size(tmp_path, review_project):
    author, _, _, _ = review_project
    data = {
        "id": "yaml-source",
        "version": "1.0",
        "kind": "still",
        "paths": [{"root_id": "sources", "path": "background.png"}],
        "provenance": {"origin": "synthetic", "commercial_use": "pending"},
    }
    path = request(tmp_path, data, "import.yaml")
    imported = invoke(
        tmp_path,
        "asset",
        "import",
        author.store.root,
        path,
        "--root",
        f"sources={tmp_path / 'Test originals 東京'}",
    )
    assert imported["id"] == "yaml-source" and imported["approval"]["status"] == "draft"
    # Bounded reading must reject before validation/import even for a large regular file.
    path.write_bytes(b" " * (16 * 1024**2 + 1))
    invoke(tmp_path, "asset", "import", author.store.root, path, expected=4)
