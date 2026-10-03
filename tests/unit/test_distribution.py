import json
import runpy
from pathlib import Path
from types import SimpleNamespace

import pytest

from tabi.api.installation import setup_check
from tabi.cli.main import main

SUPPORT = runpy.run_path(str(Path(__file__).resolve().parents[2] / "scripts/package_support.py"))


def built(tmp_path):
    (tmp_path / "web/src").mkdir(parents=True)
    (tmp_path / "web/src/main.ts").write_text("// Test source")
    (tmp_path / "web/dist/assets").mkdir(parents=True)
    (tmp_path / "web/dist/index.html").write_text("<!doctype html>Test static build")
    (tmp_path / "web/dist/assets/app.js").write_text("'use strict';")
    (tmp_path / "pyproject.toml").write_text('[project]\nversion="0.1.0"\n')
    for name in (
        "ajv",
        "ajv-formats",
        "fast-uri",
        "fast-deep-equal",
        "json-schema-traverse",
        "require-from-string",
    ):
        directory = tmp_path / "web/node_modules" / name
        directory.mkdir(parents=True)
        (directory / "package.json").write_text(
            json.dumps({"version": "fixture", "license": "test-only"})
        )
        (directory / "LICENSE").write_text("Synthetic build-check fixture, never distributed.")
    SUPPORT["stamp_frontend"](tmp_path)
    return tmp_path / "web/dist"


def test_distribution_refuses_stale_sources_changed_output_and_unreviewed_binaries(tmp_path):
    output = built(tmp_path)
    assert SUPPORT["verify_frontend"](tmp_path)["version"] == "0.1.0"
    (output / "assets/app.js").write_text("changed")
    with pytest.raises(ValueError, match="hash mismatch"):
        SUPPORT["verify_frontend"](tmp_path)
    SUPPORT["stamp_frontend"](tmp_path)
    (tmp_path / "web/src/main.ts").write_text("changed source")
    with pytest.raises(ValueError, match="sources changed"):
        SUPPORT["verify_frontend"](tmp_path)
    (output / "private.MP4").write_bytes(b"not media")
    SUPPORT["stamp_frontend"](tmp_path)
    with pytest.raises(ValueError, match="must not enter"):
        SUPPORT["verify_frontend"](tmp_path)


def test_setup_check_reports_corrupt_frontend_and_keeps_dependency_instructions(
    tmp_path, monkeypatch
):
    output = built(tmp_path)
    media = {
        "issues": [{"message": "FFmpeg missing", "suggested_fix": "Install FFmpeg externally"}]
    }
    monkeypatch.setattr("tabi.api.installation.default_web_root", lambda: output)
    monkeypatch.setattr(
        "tabi.api.installation.doctor",
        lambda *args: SimpleNamespace(ready=False, model_dump=lambda **kwargs: media),
    )
    report = setup_check(None, tmp_path)
    assert not report["ready"] and report["frontend"]["verified"]
    assert report["media"]["issues"][0]["suggested_fix"] == "Install FFmpeg externally"
    (output / "assets/app.js").write_text("tampered")
    report = setup_check(None, tmp_path)
    assert "hash changed" in report["problems"][0] and not report["frontend"]["verified"]


def test_first_launch_creates_only_the_configured_default_project_root(tmp_path, monkeypatch):
    root = tmp_path / "New projects 東京"
    monkeypatch.setenv("TABI_PROJECT_ROOT", str(root))
    launched = []
    monkeypatch.setattr(
        "tabi.api.launcher.launch", lambda settings, roots, **kwargs: launched.append(roots) or 0
    )
    assert main(["web", "--no-open"]) == 0
    assert root.is_dir() and launched == [{"projects": root}]
