import json
import struct
from types import SimpleNamespace

import pytest

from tabi.cli.main import main
from tabi.core.render.backend import RenderError
from tabi.core.render.mp4 import verify_fast_start
from tabi.core.render.profiles import preset_profile, require_encoder, video_arguments


def box(kind, payload=b"", *, extended=False):
    return (
        struct.pack(">I4sQ", 1, kind, len(payload) + 16)
        if extended
        else struct.pack(">I4s", len(payload) + 8, kind)
    ) + payload


def test_mp4_layout_checks_boundaries_and_metadata_order_without_loading_payloads(tmp_path):
    path = tmp_path / "test.mp4"
    path.write_bytes(box(b"ftyp") + box(b"moov", extended=True) + box(b"mdat", b"samples"))
    verified = verify_fast_start(path)
    assert verified.fast_start and verified.moov_offset == 8 and verified.first_mdat_offset == 24
    for invalid in (
        box(b"ftyp") + box(b"mdat") + box(b"moov"),
        box(b"ftyp") + box(b"moov") + box(b"moov") + box(b"mdat"),
        struct.pack(">I4s", 1, b"moov") + b"short",
        struct.pack(">I4s", 7, b"moov"),
        struct.pack(">I4s", 1000, b"mdat"),
        b"truncated",
    ):
        path.write_bytes(invalid)
        with pytest.raises(RenderError):
            verify_fast_start(path)


def test_presets_preserve_rational_source_rate_and_explicit_encoder(capsys):
    assert main(["profiles", "--fps-num", "30000", "--fps-den", "1001"]) == 0
    presets = json.loads(capsys.readouterr().out)
    assert [p["canvas"]["width"] for p in presets] == [960, 1920, 3840]
    assert all(p["fps"] == {"num": 30000, "den": 1001} for p in presets)
    assert presets[-1]["video_bitrate"] == 40000000 and presets[-1]["audio_bitrate"] == 384000
    assert preset_profile("1080p", fps={"num": 60, "den": 1}).video_bitrate == 12000000
    profile = preset_profile("4k", encoder="h264_videotoolbox", video_bitrate=50000000)
    args = video_arguments(profile)
    assert args[args.index("-allow_sw") + 1] == "0"
    assert args[args.index("-bf") + 1] == "0"
    assert args[args.index("-b:v") + 1] == "50000000"
    with pytest.raises(RenderError, match="unavailable"):
        require_encoder(SimpleNamespace(encoders=["libx264", "aac"]), profile)
    for name, encoder in (("8k", "libx264"), ("proxy", "automatic")):
        with pytest.raises(RenderError):
            preset_profile(name, encoder=encoder)
    with pytest.raises(ValueError):
        preset_profile("proxy", video_bitrate=0)
