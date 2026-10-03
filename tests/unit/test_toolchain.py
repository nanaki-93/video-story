import json
import shutil
import sys

import pytest

from tabi.core import toolchain
from tabi.core.config import load_settings
from tabi.core.documents import parse_document
from tabi.core.models.diagnostics import ToolInfo
from tabi.core.process import ToolError, run_tool


@pytest.fixture
def settings(tmp_path):
    return load_settings(None, env={}, cwd=tmp_path, home=tmp_path)


@pytest.fixture
def fake_tools(monkeypatch, tmp_path):
    def probe(name, requested):
        return ToolInfo(
            requested=requested, path=str(tmp_path / name), version="test-1", sha256="a" * 64
        ), []

    def run(args, **kwargs):
        if "-filters" in args:
            return "\n".join(
                f" TS {name} V->V description" for name in toolchain.REQUIRED_FILTERS
            ).encode()
        if "-encoders" in args:
            return (
                b" V....D libx264 description\n A..... aac description\n"
                b" V....D h264_videotoolbox description"
            )
        if "-hwaccels" in args:
            return b"Hardware acceleration methods:\nvideotoolbox\n"
        return b"0"

    monkeypatch.setattr(toolchain, "probe_tool", probe)
    monkeypatch.setattr(toolchain, "run_tool", run)
    return run


def test_listing_parser_accepts_two_and_three_flags_and_ignores_legends():
    output = (
        " T.. = Timeline support\n TS overlay VV->V overlay\n"
        " TSC crop V->V crop\n .. scale V->V scale\n"
    )
    assert toolchain.parse_listing(output, "filters") == ["crop", "overlay", "scale"]
    assert toolchain.parse_listing(
        " V..... = Video\n V....D libx264 description\n A..... aac description", "encoders"
    ) == ["aac", "libx264"]


def test_missing_tool_explains_install_and_configuration(tmp_path):
    report, issues = toolchain.probe_tool("ffmpeg", str(tmp_path / "missing ffmpeg"))
    assert report.version is None and report.path is None
    assert issues[0].code == "tool_missing"
    assert "TABI_FFMPEG" in issues[0].suggested_fix and "brew install" in issues[0].suggested_fix


def test_wrong_executable_is_not_mistaken_for_ffmpeg():
    report, issues = toolchain.probe_tool("ffmpeg", sys.executable)
    assert report.version is None and issues[0].code == "tool_probe_failed"


def test_ready_report_still_does_not_claim_hardware_render(settings, tmp_path, fake_tools):
    report = toolchain.doctor(settings, tmp_path)
    assert report.ready and report.encoder_verification == "listed_only"
    assert "h264_videotoolbox" in report.encoders
    assert parse_document(report.model_dump_json()) == report
    assert not list(tmp_path.iterdir())
    again = toolchain.doctor(settings, tmp_path)
    assert again.fingerprint == report.fingerprint


def test_missing_filter_and_mismatched_tool_versions_fail(
    settings, tmp_path, fake_tools, monkeypatch
):
    def run(args, **kwargs):
        return b" .. fps V->V frame rate\n" if "-filters" in args else fake_tools(args)

    def probe(name, requested):
        return ToolInfo(
            requested=requested, path=name, version="9.0" if name == "ffmpeg" else "8.0"
        ), []

    monkeypatch.setattr(toolchain, "run_tool", run)
    monkeypatch.setattr(toolchain, "probe_tool", probe)
    report = toolchain.doctor(settings, tmp_path)
    assert not report.ready
    assert {p.code for p in report.issues} == {"capability_missing", "tool_version_mismatch"}


def test_storage_probe_missing_full_and_unwritable(tmp_path, monkeypatch):
    missing = tmp_path / "not created"
    assert toolchain.probe_storage(missing)[1][0].code == "storage_unwritable"
    assert not missing.exists()
    monkeypatch.setattr(shutil, "disk_usage", lambda _: shutil._ntuple_diskusage(100, 99, 1))
    storage, issues = toolchain.probe_storage(tmp_path)
    assert storage.writable and issues[0].code == "storage_low"

    def denied(*args, **kwargs):
        raise PermissionError("synthetic denied write")

    monkeypatch.setattr(toolchain.tempfile, "TemporaryFile", denied)
    assert toolchain.probe_storage(tmp_path)[1][0].code == "storage_unwritable"


def test_non_mac_never_claims_target_mac(monkeypatch):
    monkeypatch.setattr(toolchain.platform, "system", lambda: "Linux")
    monkeypatch.setattr(toolchain.platform, "machine", lambda: "aarch64")
    monkeypatch.setattr(toolchain.platform, "processor", lambda: "Apple M5 Pro")
    assert toolchain.machine_info().is_target_m5_pro is False


def test_process_arguments_preserve_unicode_spaces_and_shell_characters(tmp_path):
    literal = str(tmp_path / "Marco's 東京;$(touch NEVER).txt")
    result = run_tool(
        [sys.executable, "-c", "import json,sys; print(json.dumps(sys.argv[1:]))", literal]
    )
    assert json.loads(result) == [literal] and not list(tmp_path.iterdir())


@pytest.mark.parametrize("kind", ["exit", "timeout", "output_limit"])
def test_owned_process_failure_is_bounded(kind):
    scripts = {
        "exit": "import sys; sys.stderr.write('useful failure'); sys.exit(7)",
        "timeout": "import time; time.sleep(10)",
        "output_limit": "print('x'*100)",
    }
    with pytest.raises(ToolError):
        run_tool(
            [sys.executable, "-c", scripts[kind]],
            timeout=0.1 if kind == "timeout" else 3,
            max_bytes=20,
        )
