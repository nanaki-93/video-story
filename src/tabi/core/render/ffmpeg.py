"""Bounded FFmpeg graphs from locked templates; filenames are always arguments."""

import hashlib
import json
import os
import tempfile
import time
from fractions import Fraction
from pathlib import Path

from PIL import Image

from ..assets import AssetService
from ..config import Settings
from ..models import CompiledSnapshot
from ..models.base import Canvas, content_hash
from ..models.production import OutputProfile, ScheduledAction
from ..models.rendering import RenderReport
from ..process import run_tool
from ..timeline import Timeline, loop_frame
from ..toolchain import doctor, file_hash
from .backend import FrozenRegistry, RenderError, backend_fingerprint
from .normalize import ImageNormalizer
from .synthetic import label as bitmap_text


class GraphBuilder:
    def __init__(self, registry: FrozenRegistry, root: Path, canvas: Canvas):
        self.registry, self.root, self.canvas = registry, root, canvas
        self.normalizer = ImageNormalizer(registry, root / "normalized")
        self.timeline = Timeline(registry.snapshot.episode)
        self.rate = registry.snapshot.episode.fps
        self.rate_text = f"{self.rate.num}/{self.rate.den}"
        self.inputs, self.filters, self.counter = [], [], 0

    def label(self):
        self.counter += 1
        return f"v{self.counter}"

    def filter(self, text):
        self.filters.append(text)

    def input(self, path: Path, *, loop: bool = True) -> str:
        if len(self.inputs) >= 128:
            raise RenderError(
                "bounded graph exceeds 128 media inputs; choose a shorter render range"
            )
        index = len(self.inputs)
        self.inputs.append((path, loop))
        return f"{index}:v"

    def still(self, ref) -> tuple[str, tuple[int, int]]:
        asset = self.registry.get(ref, "asset")
        if asset.kind not in {"still", "mask"}:
            raise RenderError("static slot requires a still or mask asset")
        path = self.normalizer.prepare(asset)
        with Image.open(path) as source:
            size = source.size
        stream, out = self.input(path), self.label()
        self.filter(f"[{stream}]format=rgba,setparams=alpha_mode=straight[{out}]")
        return out, size

    def overlay(self, base, layer, *, x=0, y=0, enable="1"):
        out = self.label()
        self.filter(
            f"[{base}][{layer}]overlay=x='{x}':y='{y}':enable='{enable}':format=rgb:alpha=straight:eof_action=pass:repeatlast=0[{out}]"
        )
        return out

    def mask_and_opacity(self, stream, slot, size):
        if slot.mask:
            mask = self.registry.get(slot.mask, "asset")
            if mask.kind != "mask":
                raise RenderError("slot mask reference is not a grayscale mask")
            path = self.normalizer.prepare(mask)
            with Image.open(path) as image:
                if image.size != size:
                    raise RenderError("mask canvas differs from its positioned layer")
            raw, color, alpha_source, alpha, gray, multiplied, result = [
                self.label() for _ in range(7)
            ]
            mask_input = self.input(path)
            self.filter(f"[{stream}]format=rgba[{raw}]")
            self.filter(f"[{raw}]split[{color}][{alpha_source}]")
            self.filter(f"[{alpha_source}]alphaextract[{alpha}]")
            self.filter(f"[{mask_input}]format=gray[{gray}]")
            self.filter(f"[{alpha}][{gray}]blend=all_mode=multiply[{multiplied}]")
            self.filter(
                f"[{color}][{multiplied}]alphamerge,setparams=alpha_mode=straight[{result}]"
            )
            stream = result
        if slot.opacity != 1:
            out = self.label()
            self.filter(
                f"[{stream}]colorchannelmixer=aa={slot.opacity:.17g},setparams=alpha_mode=straight[{out}]"
            )
            stream = out
        return stream

    def action(self, event: ScheduledAction, start: int, end: int):
        left, right = max(start, event.start_frame), min(end, event.end_frame)
        asset = self.registry.get(event.clip, "asset")
        folder = self.root / f"clip-{self.counter}-{len(self.inputs)}"
        folder.mkdir()
        for local, frame in enumerate(range(left, right)):
            source_frame = (
                loop_frame(frame, event.phase_origin_frame, event.loop)
                if event.loop
                else event.source_start_frame + frame - event.start_frame
            )
            prepared = self.normalizer.prepare(asset, source_frame)
            os.link(prepared, folder / f"{local:06}.png")
        stream, result = self.input(folder / "%06d.png", loop=False), self.label()
        offset = f"{(left - start) * self.rate.den}/{self.rate.num}"
        self.filter(
            f"[{stream}]format=rgba,setparams=alpha_mode=straight,setpts=PTS-STARTPTS+({offset})/TB[{result}]"
        )
        return result, left - start, right - start

    def scene(self, scene, start, end):
        template = self.registry.get(scene.template, "scene_template")
        width, height = template.design_canvas.width, template.design_canvas.height
        base = self.label()
        self.filter(
            f"color=c=black:s={width}x{height}:r={self.rate_text},format=rgba,"
            f"trim=end_frame={end - start},setpts=PTS-STARTPTS[{base}]"
        )
        for slot in template.slots:
            if slot.kind == "still":
                ref = scene.slot_assignments.get(slot.id, slot.asset)
                if ref is None:
                    raise RenderError(f"static slot {slot.id} has no asset")
                layer, size = self.still(ref)
                if size != (width, height):
                    raise RenderError(
                        "static layer must match the design canvas after its explicit crop"
                    )
                layer = self.mask_and_opacity(layer, slot, size)
                base = self.overlay(base, layer)
            elif slot.kind == "character":
                if scene.slot_assignments.get(slot.id) is not None or slot.asset is not None:
                    raise RenderError(
                        "character slots use compiled actions, not a static asset override"
                    )
                if slot.mask is not None:
                    raise RenderError(
                        "character masks require scene-sized prepared clips in this backend"
                    )
                active = [
                    event
                    for event in self.registry.snapshot.schedule
                    if isinstance(event, ScheduledAction)
                    and event.scene_id == scene.id
                    and event.start_frame < end
                    and start < event.end_frame
                ]
                active.sort(
                    key=lambda event: (event.channel == "face", event.start_frame, event.id)
                )
                for event in active:
                    pack = self.registry.get(event.pack, "action_pack")
                    anchor = template.anchors[scene.anchor or slot.anchor]
                    layer, first, last = self.action(event, start, end)
                    layer = self.mask_and_opacity(
                        layer, slot, (pack.canvas.width, pack.canvas.height)
                    )
                    base = self.overlay(
                        base,
                        layer,
                        x=round(anchor.x - pack.anchor.x),
                        y=round(anchor.y - pack.anchor.y),
                        enable=f"gte(n,{first})*lt(n,{last})",
                    )
            else:
                raise RenderError(
                    f"unsupported slot capability: {slot.kind}; static/character rendering only"
                )
        # Fit the complete composition, preserving relative anchors and mask geometry.
        out = self.label()
        target = self.canvas
        scale = (
            min(Fraction(target.width, width), Fraction(target.height, height))
            if template.fit == "letterbox"
            else max(Fraction(target.width, width), Fraction(target.height, height))
        )
        scaled_width, scaled_height = round(width * scale), round(height * scale)
        finish = (
            f"pad={target.width}:{target.height}:(ow-iw)/2:(oh-ih)/2:color=black"
            if template.fit == "letterbox"
            else f"crop={target.width}:{target.height}:(iw-ow)/2:(ih-oh)/2"
        )
        self.filter(
            f"[{base}]scale={scaled_width}:{scaled_height}:flags=lanczos,{finish},"
            f"setsar=1,trim=end_frame={end - start},setpts=PTS-STARTPTS[{out}]"
        )
        return out

    def build(self, start, end, *, video):
        parts = []
        for scene in self.registry.snapshot.episode.scenes:
            left, right = max(start, scene.start_frame), min(end, scene.end_frame)
            if left < right:
                if scene.transition_in.kind != "cut" or scene.transition_out.kind != "cut":
                    raise RenderError("overlap rendering requires explicit T18 semantics")
                parts.append(self.scene(scene, left, right))
        base = parts[0]
        if len(parts) > 1:
            base = self.label()
            self.filter(
                "".join(f"[{part}]" for part in parts) + f"concat=n={len(parts)}:v=1:a=0[{base}]"
            )
        if self.registry.snapshot.purpose != "production":
            # Original bitmap glyphs avoid a font dependency/licence. This is always visible.
            width = min(self.canvas.width, 640)
            pixels = bytearray(bytes((40, 20, 60)) * width * 28)
            bitmap_text(
                pixels,
                width,
                "SYNTHETIC TEST"
                if self.registry.snapshot.purpose == "synthetic_test"
                else "DRAFT PREVIEW",
                8,
                6,
                scale=2,
            )
            badge = self.root / "badge.png"
            Image.frombytes("RGB", (width, 28), bytes(pixels)).save(badge)
            base = self.overlay(base, self.input(badge), y=max(0, self.canvas.height - 28))
        if video:
            self.filter(
                f"[{base}]fps={self.rate_text},trim=end_frame={end - start},setpts=PTS-STARTPTS,"
                "scale=in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p,"
                "setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709[output]"
            )
        else:
            self.filter(f"[{base}]format=rgb24[output]")
        return ";\n".join(self.filters)


def verify_video(settings, path, profile, frames):
    probe = json.loads(
        run_tool(
            [
                settings.ffprobe,
                "-v",
                "error",
                "-count_frames",
                "-show_streams",
                "-of",
                "json",
                str(path),
            ],
            timeout=300,
        )
    )
    if len(probe.get("streams", [])) != 1:
        raise RenderError("video-only render has unexpected streams")
    stream = probe["streams"][0]
    if (
        stream.get("codec_name"),
        stream.get("pix_fmt"),
        stream.get("width"),
        stream.get("height"),
        int(stream.get("nb_read_frames", 0)),
    ) != ("h264", "yuv420p", profile.canvas.width, profile.canvas.height, frames):
        raise RenderError("encoded video does not match its requested profile/frame count")
    if Fraction(stream["avg_frame_rate"]) != Fraction(profile.fps.num, profile.fps.den):
        raise RenderError("encoded frame rate differs from profile")
    if (
        any(
            stream.get(key) != "bt709"
            for key in ("color_space", "color_transfer", "color_primaries")
        )
        or stream.get("color_range") != "tv"
    ):
        raise RenderError("encoded video lacks explicit BT.709 limited-range tags")
    timing = json.loads(
        run_tool(
            [
                settings.ffprobe,
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_frames",
                "-show_entries",
                "frame=best_effort_timestamp",
                "-of",
                "json",
                str(path),
            ],
            timeout=300,
            max_bytes=16 * 1024 * 1024,
        )
    )
    timestamps = [
        int(frame["best_effort_timestamp"]) * Fraction(stream["time_base"])
        for frame in timing["frames"]
    ]
    if len(timestamps) != frames or any(
        abs(stamp - Fraction(n * profile.fps.den, profile.fps.num)) > Fraction(stream["time_base"])
        for n, stamp in enumerate(timestamps)
    ):
        raise RenderError("encoded timestamps do not follow the exact frame schedule")
    run_tool(
        [settings.ffmpeg, "-v", "error", "-xerror", "-nostdin", "-i", str(path), "-f", "null", "-"],
        timeout=300,
    )


class FFmpegRenderer:
    capabilities = frozenset(
        {
            "still",
            "character",
            "grayscale_mask",
            "straight_alpha",
            "premultiplied_input",
            "cut",
            "letterbox",
            "crop",
        }
    )

    def __init__(self, assets: AssetService, settings: Settings):
        self.assets, self.settings = assets, settings

    def frame(self, snapshot, frame, output, *, canvas=None):
        return self._render(
            snapshot, frame, frame + 1, output, canvas or snapshot.episode.canvas, None
        )

    def clip(self, snapshot, start, end, output, profile):
        profile = OutputProfile.model_validate(profile)
        if (
            profile.fps != snapshot.episode.fps
            or profile.container != "mp4"
            or profile.pixel_format != "yuv420p"
            or profile.video_codec not in {"libx264", "h264_videotoolbox"}
            or profile.audio_codec is not None
        ):
            raise RenderError(
                "backend requires matching fps and video-only H.264/YUV420P MP4; "
                "audio mixing follows in T16"
            )
        if profile.canvas.width % 2 or profile.canvas.height % 2:
            raise RenderError("H.264 YUV420P needs even output dimensions")
        return self._render(snapshot, start, end, output, profile.canvas, profile)

    def _render(self, snapshot, start, end, output, canvas, profile):
        snapshot = CompiledSnapshot.model_validate(snapshot)
        canvas = Canvas.model_validate(canvas)
        if snapshot.purpose != "production" and (canvas.width < 168 or canvas.height < 28):
            raise RenderError("draft preview canvas must fit its 168×28 review label")
        if (
            type(start) is not int
            or type(end) is not int
            or not 0 <= start < end <= snapshot.episode.duration_frames
        ):
            raise RenderError("render range must be nonempty and inside the episode")
        if end - start > 7200:
            raise RenderError(
                "bounded render supports at most 7,200 frames; plan chunks for longer ranges"
            )
        output = output.expanduser().absolute()
        if output.exists() or output.is_symlink():
            raise RenderError("output exists; choose a new file")
        if output.suffix.lower() != (".mp4" if profile else ".png"):
            raise RenderError("output extension does not match the requested media")
        output.parent.mkdir(parents=True, exist_ok=True)
        capabilities = doctor(self.settings, output.parent)
        if not capabilities.ready:
            raise RenderError("media tools/storage are not ready; run tabi doctor")
        registry = FrozenRegistry(self.assets, snapshot)
        with tempfile.TemporaryDirectory(prefix=".tabi-render-", dir=output.parent) as scratch:
            root = Path(scratch)
            builder = GraphBuilder(registry, root, canvas)
            graph = builder.build(start, end, video=profile is not None)
            graph_path = root / "graph.txt"
            graph_path.write_text(graph)
            temporary = root / output.name
            args = [
                self.settings.ffmpeg,
                "-v",
                "error",
                "-nostdin",
                "-n",
                "-filter_complex_threads",
                "1",
            ]
            for path, loop in builder.inputs:
                if loop:
                    args.extend(["-loop", "1"])
                args.extend(["-framerate", builder.rate_text, "-i", str(path)])
            args.extend(
                [
                    "-/filter_complex",
                    str(graph_path),
                    "-map",
                    "[output]",
                    "-frames:v",
                    str(end - start),
                    "-an",
                ]
            )
            if profile:
                args.extend(
                    [
                        "-fps_mode",
                        "cfr",
                        "-c:v",
                        profile.video_codec,
                        "-g",
                        "60",
                        "-pix_fmt",
                        "yuv420p",
                    ]
                )
                args.extend(
                    ["-preset", "veryfast"]
                    + (
                        ["-b:v", str(profile.video_bitrate)]
                        if profile.video_bitrate
                        else ["-crf", "16"]
                    )
                    if profile.video_codec == "libx264"
                    else ["-allow_sw", "0", "-b:v", str(profile.video_bitrate or 8000000)]
                )
                args.extend(
                    [
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
                )
            else:
                args.extend(["-update", "1", "-c:v", "png"])
            args.append(str(temporary))
            began = time.monotonic()
            run_tool(args, timeout=600)
            elapsed = time.monotonic() - began
            if profile:
                verify_video(self.settings, temporary, profile, end - start)
            else:
                with Image.open(temporary) as image:
                    image.load()
                    if image.size != (canvas.width, canvas.height) or image.mode != "RGB":
                        raise RenderError("still output failed canvas/pixel verification")
            registry.verify()
            report = RenderReport(
                schema_version="1.0",
                purpose=snapshot.purpose,
                snapshot_sha256=content_hash(snapshot),
                first_frame=start,
                frame_count=end - start,
                canvas=canvas,
                fps=snapshot.episode.fps,
                output=str(output),
                output_sha256=file_hash(temporary),
                output_bytes=temporary.stat().st_size,
                graph_sha256=hashlib.sha256(graph.encode()).hexdigest(),
                backend=backend_fingerprint(),
                toolchain_fingerprint=capabilities.fingerprint,
                render_seconds=elapsed,
                full_decode_passed=True,
                timestamps_verified=bool(profile),
                normalized_images=len(builder.normalizer.prepared),
                warnings=sorted(builder.normalizer.warnings),
            )
            with temporary.open("rb") as source:
                os.fsync(source.fileno())
            os.link(temporary, output)
            descriptor = os.open(output.parent, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
            return report
