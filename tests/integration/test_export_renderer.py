import numpy as np
import pytest
from PIL import Image
from test_chunk_assembly import setup

from tabi.core.jobs.planner import video_profile
from tabi.core.process import run_tool
from tabi.core.render.ffmpeg import FFmpegRenderer
from tabi.core.render.profiles import preset_profile
from tabi.core.toolchain import doctor

pytestmark = pytest.mark.media


@pytest.mark.parametrize("encoder", ["libx264", "h264_videotoolbox"])
@pytest.mark.parametrize("preset", ["proxy", "1080p", "4k"])
def test_export_preset_decodes_with_color_audio_fast_start_and_reference_quality(
    tmp_path, encoder, preset
):
    service, snapshot, digest, _ = setup(tmp_path, "effects")
    capabilities = doctor(service.settings, service.store.root)
    if encoder not in capabilities.encoders:
        pytest.skip(f"explicit encoder {encoder} unavailable on this machine")
    profile = preset_profile(preset, fps=snapshot.episode.fps, encoder=encoder)
    service.submit(
        digest, profile, "exports/preset.mp4", first_frame=140, end_frame=164, max_chunk_frames=12
    )
    job = service.work()[0]
    assert job.state == "verified", job.error
    verified = service.verify_export(job.id)
    assert verified.video.canvas == profile.canvas
    assert verified.video.profile == "High" and verified.video.progressive
    assert verified.video.frame_count == 24 and verified.video.duration_seconds == 0.8
    assert verified.video.mp4.moov_offset < verified.video.mp4.first_mdat_offset
    assert verified.audio.intended_samples == 38400
    actual = tmp_path / "decoded.png"
    run_tool(
        [
            service.settings.ffmpeg,
            "-v",
            "error",
            "-i",
            str(service.store.root / job.destination),
            "-vf",
            "select=eq(n\\,11),scale=in_color_matrix=bt709:in_range=tv:out_range=pc,format=rgb24",
            "-frames:v",
            "1",
            "-update",
            "1",
            str(actual),
        ],
        timeout=60,
    )
    expected = tmp_path / "reference.png"
    FFmpegRenderer(service.assets, service.settings).frame(
        snapshot, 151, expected, canvas=profile.canvas
    )
    with Image.open(actual) as image, Image.open(expected) as reference:
        difference = np.abs(
            np.asarray(image).astype(np.int16) - np.asarray(reference).astype(np.int16)
        )
        assert float(np.mean(difference)) < 3
        assert float(np.quantile(difference, 0.99)) < 24
    output = service.store.root / job.destination
    with output.open("r+b") as stream:
        stream.truncate(output.stat().st_size // 2)
    with pytest.raises(ValueError, match="bytes differ"):
        service.verify_export(job.id)


def test_hardware_short_chunks_and_fractional_rate_keep_exact_timing(tmp_path):
    service, snapshot, _, _ = setup(tmp_path, "core", fractional=True)
    if "h264_videotoolbox" not in doctor(service.settings, service.store.root).encoders:
        pytest.skip("VideoToolbox unavailable on this machine")
    profile = video_profile(
        preset_profile("4k", fps=snapshot.episode.fps, encoder="h264_videotoolbox")
    )
    renderer = FFmpegRenderer(service.assets, service.settings)
    for count in (1, 2, 3, 11, 12, 13, 37):
        report = renderer.clip(snapshot, 0, count, tmp_path / f"short-{count}.mp4", profile)
        assert report.video_verification.frame_count == count
        assert report.video_verification.fps == snapshot.episode.fps
