import json
import os
import subprocess
import sys

import yaml


def run_cli(tmp_path, *args):
    env = {key: value for key, value in os.environ.items() if not key.startswith("TABI_")}
    env["XDG_CONFIG_HOME"] = str(tmp_path / "config")
    return subprocess.run(
        [sys.executable, "-m", "tabi", *args],
        env=env,
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )


def test_machine_output_and_logs_use_separate_streams(tmp_path):
    result = run_cli(tmp_path, "config", "--json")
    assert result.returncode == 0
    assert json.loads(result.stdout)["config_loaded"] is False
    assert json.loads(result.stderr)["event"] == "configuration_resolved"


def test_configuration_failure_has_usage_exit_code(tmp_path):
    result = run_cli(tmp_path, "--config", "missing.toml", "config", "--json")
    assert result.returncode == 2
    assert result.stdout == ""
    assert "does not exist" in json.loads(result.stderr)["event"]


def test_help_and_version_work_without_config(tmp_path):
    for args in [("--help",), ("--version",)]:
        result = run_cli(tmp_path, "--config", "missing.toml", *args)
        assert result.returncode == 0
        assert result.stdout
        assert result.stderr == ""


def test_unimplemented_media_command_is_not_exposed(tmp_path):
    result = run_cli(tmp_path, "render")
    assert result.returncode == 2
    assert result.stdout == ""


def test_project_init_and_reopen_preserve_unicode_paths_and_state(tmp_path):
    root = tmp_path / "Marco's 東京 project"
    created = run_cli(
        tmp_path, "project", "init", str(root), "--title", "Synthetic 日本語 project", "--json"
    )
    assert created.returncode == 0 and created.stderr == ""
    project = json.loads(created.stdout)
    assert project["title"] == "Synthetic 日本語 project" and project["revision"] == 0
    assert project["root"] == "."
    reopened = run_cli(tmp_path, "project", "show", str(root), "--json")
    assert reopened.returncode == 0 and json.loads(reopened.stdout) == project
    original = (root / "project.json").read_bytes()
    repeated = run_cli(tmp_path, "project", "init", str(root), "--title", "Must not overwrite")
    assert repeated.returncode == 2
    assert "existing files are preserved" in json.loads(repeated.stderr)["event"]
    assert (root / "project.json").read_bytes() == original


def test_project_missing_file_has_io_exit_code(tmp_path):
    result = run_cli(tmp_path, "project", "show", str(tmp_path), "--json")
    assert result.returncode == 4 and result.stdout == ""
    assert "project_io_error" in json.loads(result.stderr)["event"]


def test_project_show_rejects_an_episode_as_the_project_index(tmp_path, episode_data):
    (tmp_path / "project.json").write_text(json.dumps(episode_data))
    result = run_cli(tmp_path, "project", "show", str(tmp_path), "--json")
    assert result.returncode == 2 and result.stdout == ""
    assert "not a project index" in json.loads(result.stderr)["event"]


def test_document_validate_accepts_json_and_yaml_with_structural_scope(tmp_path, project_data):
    for name, payload in [
        ("project.json", json.dumps(project_data)),
        ("project.yaml", yaml.safe_dump(project_data)),
    ]:
        path = tmp_path / name
        path.write_text(payload)
        result = run_cli(tmp_path, "document", "validate", str(path))
        assert result.returncode == 0 and result.stderr == ""
        report = json.loads(result.stdout)
        assert report["valid"] is True and report["scope"] == "structure"
        assert report["issues"] == []


def test_document_validate_reports_nested_error_without_a_traceback(tmp_path, episode_data):
    episode_data["scenes"][0]["unexpected"] = True
    path = tmp_path / "invalid.json"
    path.write_text(json.dumps(episode_data))
    result = run_cli(tmp_path, "document", "validate", str(path))
    assert result.returncode == 2 and result.stderr == ""
    report = json.loads(result.stdout)
    assert report["valid"] is False and report["scope"] == "structure"
    assert any(issue["location"] == ["scenes", 0, "unexpected"] for issue in report["issues"])


def test_document_missing_file_has_io_exit_code(tmp_path):
    result = run_cli(tmp_path, "document", "validate", "missing.json")
    assert result.returncode == 4 and result.stdout == ""
    assert "document_io_error" in json.loads(result.stderr)["event"]


def test_doctor_missing_dependency_reports_actionable_json(tmp_path):
    config = tmp_path / "missing-tools.toml"
    config.write_text(
        'schema_version = "1.0"\n[tools]\nffmpeg = "./missing ffmpeg"\n'
        'ffprobe = "./missing ffprobe"\n'
    )
    result = run_cli(tmp_path, "--config", str(config), "doctor", "--json")
    assert result.returncode == 3
    report = json.loads(result.stdout)
    assert report["ready"] is False and report["encoder_verification"] == "listed_only"
    assert {p["code"] for p in report["issues"]} == {"tool_missing"}
    assert all(p["suggested_fix"] for p in report["issues"])
    render = run_cli(
        tmp_path, "--config", str(config), "render-spike", "--output-dir", str(tmp_path), "--json"
    )
    assert render.returncode == 3 and render.stdout == ""
    assert "TABI_FFMPEG" in json.loads(render.stderr.splitlines()[-1])["event"]
    assert not list(tmp_path.rglob("*.mp4"))
