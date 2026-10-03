"""Explicit SDR export presets and one encoder policy shared by chunks/fallback."""

from fractions import Fraction

from ..models.base import Canvas, FrameRate
from ..models.production import OutputProfile
from .backend import RenderError

ENCODERS = ("libx264", "h264_videotoolbox")
PRESETS = {
    "proxy": (960, 540, 3_000_000),
    "1080p": (1920, 1080, 8_000_000),
    "4k": (3840, 2160, 40_000_000),
}


def preset_profile(name, *, fps=None, encoder="libx264", video_bitrate=None, audio_gain_db=0):
    if name not in PRESETS or encoder not in ENCODERS:
        raise RenderError("unknown export preset or unsupported encoder")
    fps = FrameRate.model_validate(fps or {"num": 30, "den": 1})
    if Fraction(fps.num, fps.den) > 60:
        raise RenderError("export presets support source frame rates up to 60 fps")
    width, height, bitrate = PRESETS[name]
    if Fraction(fps.num, fps.den) > 30:
        bitrate = bitrate * 3 // 2
    return OutputProfile(
        id=f"{name}-{encoder}",
        canvas=Canvas(width=width, height=height),
        fps=fps,
        container="mp4",
        video_codec=encoder,
        pixel_format="yuv420p",
        color_space="bt709",
        audio_codec="aac",
        audio_gain_db=audio_gain_db,
        audio_bitrate=192000 if name == "proxy" else 384000,
        video_bitrate=bitrate if video_bitrate is None else video_bitrate,
    )


def require_encoder(capabilities, profile):
    if profile.video_codec not in ENCODERS or profile.video_codec not in capabilities.encoders:
        raise RenderError(f"requested encoder is unavailable: {profile.video_codec}")
    if profile.audio_codec and profile.audio_codec not in capabilities.encoders:
        raise RenderError(f"requested audio encoder is unavailable: {profile.audio_codec}")


def video_arguments(profile):
    if profile.video_codec not in ENCODERS:
        raise RenderError("unsupported video encoder; choose an explicit supported encoder")
    args = [
        "-fps_mode",
        "cfr",
        "-c:v",
        profile.video_codec,
        "-profile:v",
        "high",
        "-g",
        str(max(1, round(Fraction(profile.fps.num, 2 * profile.fps.den)))),
        "-pix_fmt",
        "yuv420p",
        "-flags",
        "+cgop",
    ]
    if profile.video_codec == "libx264":
        args += ["-bf", "2", "-preset", "veryfast", "-x264-params", "open-gop=0:cabac=1"]
        args += ["-b:v", str(profile.video_bitrate)] if profile.video_bitrate else ["-crf", "14"]
    else:
        # The pinned macOS/FFmpeg VideoToolbox path produced clamped DTS and
        # one-tick sample durations with reordered B frames in short 4K chunks.
        # Disable reordering explicitly; never repair it by changing frame times.
        args += [
            "-bf",
            "0",
            "-allow_sw",
            "0",
            "-coder",
            "cabac",
            "-b:v",
            str(profile.video_bitrate or 8000000),
        ]
    return args + [
        "-color_range",
        "tv",
        "-colorspace",
        "bt709",
        "-color_primaries",
        "bt709",
        "-color_trc",
        "bt709",
        "-movflags",
        "+faststart",
    ]
