"""Decode local media before registration; never infer sequence timing."""

import json
import warnings
import wave
from fractions import Fraction
from pathlib import Path

from PIL import Image, ImageFont

from ..models.assets import ProbeData
from ..models.base import Canvas, FrameRate
from ..process import run_tool


def image_probe(path: Path, *, mask: bool = False) -> ProbeData:
    with warnings.catch_warnings():
        warnings.simplefilter("error", Image.DecompressionBombWarning)
        with Image.open(path) as image:
            image.load()
            if getattr(image, "n_frames", 1) != 1:
                raise ValueError("animated image requires an explicitly exported sequence")
            if image.getexif().get(274, 1) != 1:
                raise ValueError("apply EXIF orientation to a prepared copy before import")
            if mask and image.mode not in {"L", "1"}:
                raise ValueError(
                    "mask must be a grayscale L/1 image; no automatic gamma conversion"
                )
            if mask and image.info.get("icc_profile"):
                raise ValueError("mask ICC profiles are ambiguous; export raw grayscale coverage")
            alpha = "A" in image.getbands() or "transparency" in image.info
            return ProbeData(
                canvas=Canvas(width=image.width, height=image.height),
                frame_count=1,
                codec=image.format or "unknown",
                pixel_format=image.mode,
                color_space="grayscale"
                if mask
                else ("srgb" if "srgb" in image.info else "unknown"),
                alpha_mode="straight" if alpha else "none",
            )


def probe_media(
    paths: list[Path], kind: str, *, fps: FrameRate | None, ffprobe: str, ffmpeg: str
) -> ProbeData:
    if kind != "sequence" and len(paths) != 1:
        raise ValueError("only image sequences may contain multiple files")
    if kind in {"still", "mask", "sequence"}:
        probes = [image_probe(path, mask=kind == "mask") for path in paths]
        if any(p != probes[0] for p in probes[1:]):
            raise ValueError("sequence frames must share canvas, color, format and alpha")
        data = probes[0].model_dump()
        if kind == "sequence":
            if fps is None:
                raise ValueError(
                    "sequence source fps is required; frame order is the explicit input order"
                )
            data.update(fps=fps, frame_count=len(paths))
        elif fps is not None:
            raise ValueError("source fps is only an input for explicitly ordered image sequences")
        return ProbeData.model_validate(data)
    if fps is not None:
        raise ValueError("source fps is only an input for explicitly ordered image sequences")
    if kind == "font":
        font = ImageFont.truetype(str(paths[0]), size=16)
        font.getmask("Tabi")
        return ProbeData(codec="font")
    if kind == "audio" and paths[0].suffix.lower() == ".wav":
        # PCM WAV gives an exact integer sample count without duration rounding.
        with wave.open(str(paths[0]), "rb") as audio:
            frames = audio.getnframes()
            expected = frames * audio.getnchannels() * audio.getsampwidth()
            actual = 0
            while block := audio.readframes(65536):
                actual += len(block)
            if actual != expected:
                raise ValueError("truncated WAV: decoded samples do not match its header")
            return ProbeData(
                sample_rate=audio.getframerate(),
                duration_samples=frames,
                channels=audio.getnchannels(),
                codec="pcm_u8"
                if audio.getsampwidth() == 1
                else f"pcm_s{audio.getsampwidth() * 8}le",
            )
    stream_type = "v:0" if kind == "video" else "a:0"
    payload = json.loads(
        run_tool(
            [
                ffprobe,
                "-v",
                "error",
                "-protocol_whitelist",
                "file,pipe",
                "-select_streams",
                stream_type,
                "-count_frames",
                "-show_streams",
                "-of",
                "json",
                str(paths[0]),
            ],
            timeout=300,
        )
    )
    if len(payload.get("streams", [])) != 1:
        raise ValueError(f"no usable {kind} stream")
    stream = payload["streams"][0]
    # A probe may tolerate corrupt packets; require a full strict decode too.
    run_tool(
        [
            ffmpeg,
            "-v",
            "error",
            "-xerror",
            "-nostdin",
            "-protocol_whitelist",
            "file,pipe",
            "-i",
            str(paths[0]),
            "-map",
            f"0:{stream_type}",
            "-f",
            "null",
            "-",
        ],
        timeout=300,
    )
    if kind == "audio":
        raise ValueError(
            "import audio as a PCM WAV master; compressed sample boundaries are not inferred"
        )
    rate = Fraction(stream["avg_frame_rate"])
    if rate != Fraction(stream["r_frame_rate"]):
        raise ValueError("variable frame rate needs explicit preparation before import")
    # Inspect every timestamp instead of trusting the header's average rate.
    timing = json.loads(
        run_tool(
            [
                ffprobe,
                "-v",
                "error",
                "-protocol_whitelist",
                "file,pipe",
                "-select_streams",
                "v:0",
                "-show_frames",
                "-show_entries",
                "frame=best_effort_timestamp",
                "-of",
                "json",
                str(paths[0]),
            ],
            timeout=300,
            max_bytes=32 * 1024 * 1024,
        )
    )
    ticks = [int(frame["best_effort_timestamp"]) for frame in timing["frames"]]
    step = 1 / rate / Fraction(stream["time_base"])
    if not ticks or any(
        abs(Fraction(tick - ticks[0]) - index * step) > 1 for index, tick in enumerate(ticks)
    ):
        raise ValueError("video timestamps are not a constant frame schedule")
    if len(ticks) != int(stream["nb_read_frames"]):
        raise ValueError("video decoded frame count does not match probe")
    pixel_aspect = Fraction(stream.get("sample_aspect_ratio", "1:1").replace(":", "/"))
    pixel = stream.get("pix_fmt", "unknown")
    return ProbeData(
        canvas=Canvas(width=stream["width"], height=stream["height"]),
        fps=FrameRate(num=rate.numerator, den=rate.denominator),
        frame_count=len(ticks),
        codec=stream.get("codec_name"),
        pixel_format=pixel,
        color_space="bt709" if stream.get("color_space") == "bt709" else "unknown",
        alpha_mode="unknown" if ("a" in pixel and pixel != "gray") else "none",
        pixel_aspect=FrameRate(num=pixel_aspect.numerator, den=pixel_aspect.denominator),
    )
