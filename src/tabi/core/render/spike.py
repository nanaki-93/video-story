"""Render and verify a bounded 10-second synthetic capability experiment."""

import json
import math
import os
import sys
import tempfile
import time
from array import array
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path

from ..config import Settings
from ..models.diagnostics import CapabilityReport, RenderSpikeReport, SpikeVerification
from ..process import ToolError, run_tool
from ..toolchain import doctor, file_hash
from .synthetic import FPS, FRAMES, HEIGHT, PALETTE, WIDTH, expected_pixel, generate_inputs, png

ENCODERS = ("libx264", "h264_videotoolbox")
SAMPLE_FRAMES = (0, 59, 60, 89, 90, 179, 180, 181, 239, 240, 299)
RGB_TOLERANCE = 12


class SpikeError(ValueError):
    pass


class SpikeDependencyError(SpikeError):
    pass


def graph() -> str:
    # Only fixed numeric fixture parameters occur here. Filenames are process
    # arguments, never interpolated into FFmpeg filter syntax.
    return "\n".join(
        [
            "[0:v]format=rgb24[cabin];",
            "[1:v]format=rgb24,crop=960:540:x='if(lt(n,90),2*n,if(lt(n,180),180,180+4*(n-180)))':y=0[strip];",
            "[2:v]format=gray[mask];",
            "[strip][mask]alphamerge[window];",
            "[cabin][window]overlay=shortest=1:format=rgb:alpha=straight[view];",
            "[3:v]format=rgba,setparams=alpha_mode=straight[actor];",
            "[view][actor]overlay=x=380:y=250:enable='gte(n,60)*lt(n,240)':format=rgb:alpha=straight[character];",
            "[4:v]format=rgba,setparams=alpha_mode=straight[front];",
            "[character][front]overlay=shortest=1:format=rgb:alpha=straight,",
            "fps=30,trim=end_frame=300,setpts=PTS-STARTPTS,",
            "scale=in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p,",
            "setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709[video]",
        ]
    )


def render_arguments(
    capabilities: CapabilityReport, inputs: list[Path], graph_path: Path, output: Path, encoder: str
) -> list[str]:
    if encoder not in ENCODERS:
        raise SpikeError("Unsupported spike encoder")
    args = [
        capabilities.ffmpeg.path,
        "-hide_banner",
        "-nostdin",
        "-v",
        "error",
        "-n",
        "-filter_complex_threads",
        "1",
    ]
    for path in inputs[:5]:
        args.extend(["-loop", "1", "-framerate", "30", "-i", str(path)])
    args.extend(
        [
            "-i",
            str(inputs[5]),
            "-/filter_complex",
            str(graph_path),
            "-map",
            "[video]",
            "-map",
            "5:a:0",
            "-t",
            "10",
            "-fps_mode",
            "cfr",
            "-c:v",
            encoder,
            "-g",
            "60",
        ]
    )
    if encoder == "libx264":
        args.extend(["-preset", "veryfast", "-crf", "18"])
    else:
        # Disallow VideoToolbox software fallback: a successful encode must use hardware.
        args.extend(["-allow_sw", "0", "-b:v", "8M"])
    args.extend(
        [
            "-pix_fmt",
            "yuv420p",
            "-color_range",
            "tv",
            "-colorspace",
            "bt709",
            "-color_primaries",
            "bt709",
            "-color_trc",
            "bt709",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-movflags",
            "+faststart",
            "-metadata",
            "title=SYNTHETIC TEST - NOT FOR PUBLICATION",
            str(output),
        ]
    )
    return args


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SpikeError(message)


def verify_media(capabilities: CapabilityReport, path: Path, evidence_dir: Path) -> dict:
    ffmpeg, ffprobe = capabilities.ffmpeg.path, capabilities.ffprobe.path
    probe = json.loads(
        run_tool(
            [
                ffprobe,
                "-v",
                "error",
                "-count_frames",
                "-show_streams",
                "-show_format",
                "-of",
                "json",
                str(path),
            ],
            timeout=60,
        )
    )
    videos = [s for s in probe["streams"] if s["codec_type"] == "video"]
    audios = [s for s in probe["streams"] if s["codec_type"] == "audio"]
    require(len(videos) == len(audios) == 1, "Expected one video and one audio stream")
    video, audio = videos[0], audios[0]
    require(
        video["codec_name"] == "h264" and video["pix_fmt"] == "yuv420p",
        "Incorrect video codec/pixel format",
    )
    require((video["width"], video["height"]) == (WIDTH, HEIGHT), "Incorrect canvas")
    require(int(video["nb_read_frames"]) == FRAMES, "Decoded video frame count differs from 300")
    require(Fraction(video["avg_frame_rate"]) == FPS, "Incorrect rational frame rate")
    require(
        all(video.get(k) == "bt709" for k in ["color_space", "color_transfer", "color_primaries"])
        and video.get("color_range") == "tv",
        "Missing BT.709 limited-range tags",
    )
    require(
        audio["codec_name"] == "aac"
        and int(audio["sample_rate"]) == 48000
        and audio["channels"] == 2,
        "Incorrect audio format",
    )
    for stream in (video, audio):
        require(
            abs(Fraction(stream["duration"]) - 10) <= Fraction(1, FPS),
            "Stream duration differs by more than one frame",
        )
        require(
            abs(Fraction(stream.get("start_time", "0"))) <= Fraction(1, 48000),
            "Nonzero stream origin",
        )
    timing = json.loads(
        run_tool(
            [
                ffprobe,
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_frames",
                "-show_entries",
                "frame=best_effort_timestamp_time",
                "-of",
                "json",
                str(path),
            ],
            timeout=60,
        )
    )
    require(len(timing["frames"]) == FRAMES, "Incomplete frame timestamp sequence")
    require(
        all(
            abs(Fraction(f["best_effort_timestamp_time"]) - Fraction(n, FPS))
            <= Fraction(1, 1000000)
            for n, f in enumerate(timing["frames"])
        ),
        "Frame timestamps are not continuous at 30/1 fps",
    )
    # Decode every video frame and audio packet, failing on any decoder error.
    run_tool(
        [
            ffmpeg,
            "-nostdin",
            "-v",
            "error",
            "-xerror",
            "-err_detect",
            "explode",
            "-i",
            str(path),
            "-map",
            "0:v:0",
            "-map",
            "0:a:0",
            "-f",
            "null",
            "-",
        ],
        timeout=60,
    )
    select = "+".join(f"eq(n,{n})" for n in SAMPLE_FRAMES)
    raw = run_tool(
        [
            ffmpeg,
            "-nostdin",
            "-v",
            "error",
            "-i",
            str(path),
            "-vf",
            f"select='{select}',scale=in_color_matrix=bt709:in_range=tv:out_range=pc,format=rgb24",
            "-fps_mode",
            "passthrough",
            "-f",
            "rawvideo",
            "-",
        ],
        timeout=60,
        max_bytes=len(SAMPLE_FRAMES) * WIDTH * HEIGHT * 3,
    )
    stride = WIDTH * HEIGHT * 3
    require(len(raw) == len(SAMPLE_FRAMES) * stride, "Incorrect number of sampled decoded frames")
    checks, maximum, boundary_checks, boundary_error = 0, 0, 0, 0
    points = [
        (60, 120),
        (900, 300),
        (200, 110),
        (710, 130),
        (820, 340),
        (180, 360),
        (450, 310),
        (408, 310),
        (388, 310),
        (450, 430),
    ]
    for index, frame in enumerate(SAMPLE_FRAMES):
        pixels = raw[index * stride : (index + 1) * stride]
        # Classify a complete stripe scanline. This resolves two-/four-pixel
        # motion at the stop/restart boundaries, beyond sparse color samples.
        observed_labels, expected_labels = [], []
        for x in range(132, 828):
            offset = (140 * WIDTH + x) * 3
            rgb = pixels[offset : offset + 3]
            observed_labels.append(
                min(
                    range(6),
                    key=lambda i: sum((a - b) ** 2 for a, b in zip(rgb, PALETTE[i], strict=True)),
                )
            )
            expected_labels.append(PALETTE.index(expected_pixel(frame, x, 140)))
        observed_edges = [
            i
            for i in range(1, len(observed_labels))
            if observed_labels[i] != observed_labels[i - 1]
        ]
        expected_edges = [
            i
            for i in range(1, len(expected_labels))
            if expected_labels[i] != expected_labels[i - 1]
        ]
        require(
            len(observed_edges) == len(expected_edges),
            f"Unexpected stripe boundaries at frame {frame}",
        )
        errors = [abs(a - b) for a, b in zip(observed_edges, expected_edges, strict=True)]
        require(max(errors, default=0) <= 1, f"Scrolling displacement mismatch at frame {frame}")
        boundary_checks += len(errors)
        boundary_error = max(boundary_error, max(errors, default=0))
        for x, y in points:
            offset = (y * WIDTH + x) * 3
            error = max(
                abs(a - b)
                for a, b in zip(
                    pixels[offset : offset + 3], expected_pixel(frame, x, y), strict=True
                )
            )
            require(
                error <= RGB_TOLERANCE,
                f"Mask/alpha/motion mismatch at frame {frame}, pixel ({x},{y}): error {error}",
            )
            maximum = max(maximum, error)
            checks += 1
        if frame in {0, 90, 240}:
            png(evidence_dir / f"frame-{frame:03}.png", WIDTH, HEIGHT, pixels)
    pcm = run_tool(
        [
            ffmpeg,
            "-nostdin",
            "-v",
            "error",
            "-i",
            str(path),
            "-map",
            "0:a:0",
            "-c:a",
            "pcm_s16le",
            "-f",
            "s16le",
            "-",
        ],
        timeout=60,
        max_bytes=4 * 482000,
    )
    require(len(pcm) % 4 == 0, "PCM output is not stereo sample-aligned")
    sample_count = len(pcm) // 4
    require(
        abs(sample_count - 480000) <= 1600,
        "Decoded AAC duration differs by more than one video frame",
    )
    samples = array("h", pcm)
    if sys.byteorder != "little":
        samples.byteswap()
    tone_ratios, rms_values = [], []
    for channel in (0, 1):
        window = [v / 32768 for v in samples[96000 + channel : 192000 : 2]]
        energy = sum(v * v for v in window) / len(window)
        real = sum(v * math.cos(2 * math.pi * 440 * n / 48000) for n, v in enumerate(window)) / len(
            window
        )
        imag = sum(v * math.sin(2 * math.pi * 440 * n / 48000) for n, v in enumerate(window)) / len(
            window
        )
        rms = math.sqrt(energy)
        ratio = 2 * (real * real + imag * imag) / energy if energy else 0
        require(0.08 < rms < 0.10 and ratio > 0.97, "Synthetic 440 Hz tone missing or distorted")
        rms_values.append(rms)
        tone_ratios.append(ratio)
    (evidence_dir / "probe.json").write_text(json.dumps(probe, indent=2) + "\n")
    return {
        "decoded_frames": FRAMES,
        "sampled_frames": list(SAMPLE_FRAMES),
        "pixel_checks": checks,
        "max_rgb_error": maximum,
        "motion_boundary_checks": boundary_checks,
        "max_boundary_error_pixels": boundary_error,
        "rgb_tolerance": RGB_TOLERANCE,
        "decoded_audio_samples": sample_count,
        "audio_rms": rms_values,
        "tone_energy_ratio": tone_ratios,
        "continuous_timestamps": True,
        "full_decode_passed": True,
    }


def render_spike(settings: Settings, output_dir: Path, encoder: str = "libx264") -> Path:
    require(encoder in ENCODERS, "Unsupported spike encoder")
    root = output_dir.expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    capabilities = doctor(settings, root)
    if not capabilities.ready:
        failure = (
            SpikeError
            if any(p.code.startswith("storage_") for p in capabilities.issues)
            else SpikeDependencyError
        )
        detail = " ".join(f"{p.message} {p.suggested_fix}" for p in capabilities.issues)
        raise failure(f"Toolchain not ready: {detail}")
    if encoder not in capabilities.encoders:
        raise SpikeDependencyError(
            f"Encoder {encoder} is not listed; run tabi doctor --json or use --encoder libx264"
        )
    run_dir = Path(tempfile.mkdtemp(prefix=f"synthetic-{encoder}-", dir=root))
    temporary = run_dir / ".rendering.mp4"
    final = run_dir / "synthetic-test.mp4"
    (run_dir / "doctor.json").write_text(capabilities.model_dump_json(indent=2) + "\n")
    try:
        inputs = generate_inputs(run_dir / "inputs")
        graph_path = run_dir / "graph.txt"
        graph_path.write_text(graph())
        args = render_arguments(capabilities, inputs, graph_path, temporary, encoder)
        (run_dir / "command.json").write_text(json.dumps(args, ensure_ascii=False, indent=2) + "\n")
        start = time.monotonic()
        run_tool(args, timeout=120)
        elapsed = time.monotonic() - start
        verification = verify_media(capabilities, temporary, run_dir)
        digest, size = file_hash(temporary), temporary.stat().st_size
        report = RenderSpikeReport(
            schema_version="1.0",
            observed_at=datetime.now(UTC),
            machine=capabilities.machine,
            toolchain_fingerprint=capabilities.fingerprint,
            ffmpeg_version=capabilities.ffmpeg.version,
            encoder=encoder,
            hardware_required=encoder == "h264_videotoolbox",
            render_seconds=elapsed,
            render_fps=FRAMES / elapsed,
            output=str(final),
            output_sha256=digest,
            output_bytes=size,
            input_hashes={path.name: file_hash(path) for path in inputs},
            graph_sha256=file_hash(graph_path),
            verification=SpikeVerification(**verification),
        )
        report_temp = run_dir / ".report.tmp"
        with report_temp.open("w", encoding="utf-8") as destination:
            destination.write(report.model_dump_json(indent=2) + "\n")
            destination.flush()
            os.fsync(destination.fileno())
        with temporary.open("rb") as source:
            os.fsync(source.fileno())
        # Atomic no-clobber publication only after the actual media passes every check.
        os.link(temporary, final)
        temporary.unlink()
        report_temp.replace(run_dir / "report.json")
        descriptor = os.open(run_dir, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        return run_dir / "report.json"
    except (ToolError, SpikeError, OSError, ValueError, KeyError) as error:
        (run_dir / "failure.json").write_text(
            json.dumps({"error": str(error), "synthetic": True, "verified": False}, indent=2) + "\n"
        )
        raise SpikeError(f"Synthetic spike failed; diagnostics: {run_dir}: {error}") from error
    finally:
        temporary.unlink(missing_ok=True)
