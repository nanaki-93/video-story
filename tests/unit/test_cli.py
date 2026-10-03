import json
import os
import subprocess
import sys


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
