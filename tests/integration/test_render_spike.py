import json
import os
from pathlib import Path

import pytest

from tabi.core.config import load_settings
from tabi.core.documents import read_document
from tabi.core.models.diagnostics import RenderSpikeReport
from tabi.core.process import ToolError
from tabi.core.render import spike
from tabi.core.toolchain import doctor, file_hash

pytestmark = pytest.mark.media


@pytest.fixture(scope="module")
def settings():
    return load_settings(None, env=os.environ, cwd=Path.cwd(), home=Path.home())


@pytest.mark.parametrize("encoder", spike.ENCODERS)
def test_actual_ten_second_media(settings, tmp_path, encoder):
    if encoder == "h264_videotoolbox":
        capabilities = doctor(settings, tmp_path)
        if capabilities.machine.os != "Darwin" or encoder not in capabilities.encoders:
            pytest.skip("Optional VideoToolbox verification requires a capable Mac")
    report_path = spike.render_spike(settings, tmp_path / "Marco's 東京 renders", encoder)
    report = read_document(report_path)
    assert isinstance(report, RenderSpikeReport)
    assert report.synthetic and not report.production_approved
    assert report.verification.decoded_frames == 300
    assert report.verification.pixel_checks == 110
    assert report.verification.max_rgb_error <= 12
    assert report.verification.motion_boundary_checks > 80
    assert report.verification.max_boundary_error_pixels <= 1
    assert file_hash(Path(report.output)) == report.output_sha256
    assert report.hardware_required == (encoder == "h264_videotoolbox")
    assert not list(report_path.parent.glob("*.tmp"))
    assert not (report_path.parent / ".rendering.mp4").exists()
    if encoder == "libx264":
        truncated = tmp_path / "truncated.mp4"
        payload = Path(report.output).read_bytes()
        truncated.write_bytes(payload[: len(payload) // 2])
        with pytest.raises((spike.SpikeError, ToolError)):
            spike.verify_media(doctor(settings, tmp_path), truncated, tmp_path)


def test_verification_failure_does_not_publish_output_or_touch_other_files(
    settings, tmp_path, monkeypatch
):
    unrelated = tmp_path / "existing export.mp4"
    unrelated.write_bytes(b"owned test sentinel: preserve existing output")

    def fail(*args, **kwargs):
        raise spike.SpikeError("synthetic failed output verification")

    monkeypatch.setattr(spike, "verify_media", fail)
    with pytest.raises(spike.SpikeError, match="failed output verification"):
        spike.render_spike(settings, tmp_path)
    assert unrelated.read_bytes() == b"owned test sentinel: preserve existing output"
    assert list(tmp_path.rglob("synthetic-test.mp4")) == []
    assert list(tmp_path.rglob(".rendering.mp4")) == []
    failure = next(tmp_path.rglob("failure.json"))
    assert json.loads(failure.read_text())["verified"] is False


@pytest.mark.parametrize("defect", ["mask", "alpha", "entry", "speed"])
def test_actual_broken_composites_fail_verification(settings, tmp_path, monkeypatch, defect):
    original = spike.graph()
    broken = {
        "mask": original.replace("format=gray[mask]", "format=gray,negate[mask]"),
        "alpha": original.replace("alpha_mode=straight[actor]", "alpha_mode=premultiplied[actor]"),
        "entry": original.replace("gte(n,60)", "gte(n,59)"),
        "speed": original.replace("180+4*(n-180)", "180+2*(n-180)"),
    }[defect]
    assert broken != original
    monkeypatch.setattr(spike, "graph", lambda: broken)
    with pytest.raises(spike.SpikeError, match="mismatch|boundaries"):
        spike.render_spike(settings, tmp_path)
    assert not list(tmp_path.rglob("synthetic-test.mp4"))
