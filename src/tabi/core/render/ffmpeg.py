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
from ..audio.mix import AudioMixer, mux_aac
from ..config import Settings
from ..models import CompiledSnapshot
from ..models.base import Canvas, content_hash
from ..models.production import OutputProfile, ScheduledAction
from ..models.rendering import RenderReport, VideoVerification
from ..models.scenes import LandmarkEvent
from ..process import checkpoint, run_tool
from ..timeline import Timeline, loop_frame
from ..timeline.effects import validate_effects
from ..timeline.transitions import validate_transitions
from ..toolchain import doctor, file_hash
from .backend import FrozenRegistry, RenderError, backend_fingerprint
from .motion import distance_expression, number, value_expression
from .mp4 import verify_fast_start
from .normalize import ImageNormalizer
from .profiles import require_encoder, video_arguments
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
        if asset.compatibility.crop is not None:
            raise RenderError("cropped action clips need an explicitly prepared pack canvas/anchor")
        folder = self.root / f"clip-{self.counter}-{len(self.inputs)}"
        folder.mkdir()
        for local, frame in enumerate(range(left, right)):
            checkpoint()
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

    def tile(self, scene, slot, start, width, height):
        ref = scene.slot_assignments.get(slot.id, slot.asset)
        if ref is None:
            raise RenderError("tile slot has no asset")
        asset = self.registry.get(ref, "asset")
        if asset.kind != "still":
            raise RenderError("tile strips must be prepared static images")
        path = self.normalizer.prepare(asset)
        with Image.open(path) as image:
            if image.height != height or image.width < slot.tile_period + width:
                raise RenderError("tile strip needs design height and period + viewport width")
            first = image.crop((0, 0, width, height)).tobytes()
            repeated = image.crop((slot.tile_period, 0, slot.tile_period + width, height)).tobytes()
            if first != repeated:
                raise RenderError("strip pixels do not repeat at the declared tile period")
        source, layer = self.input(path), self.label()
        distance = distance_expression(self.timeline, scene.id, f"(n+{start})")
        # The small epsilon handles double representation at exact integer pixel boundaries.
        x = f"floor(mod(({distance})*{number(slot.depth_factor)},{slot.tile_period})+0.0000001)"
        self.filter(
            f"[{source}]format=rgba,setparams=alpha_mode=straight,crop={width}:{height}:x='{x}':y=0[{layer}]"
        )
        return self.mask_and_opacity(layer, slot, (width, height))

    def landmarks(self, scene, slot, start, end, width, height):
        if slot.asset is not None or slot.id in scene.slot_assignments:
            raise RenderError(
                "scheduled sprite media is selected by its event, not a slot override"
            )
        slots = [
            s
            for s in self.registry.get(scene.template, "scene_template").slots
            if s.kind == "scheduled_sprite"
        ]
        events = [
            e
            for e in self.registry.snapshot.schedule
            if isinstance(e, LandmarkEvent) and e.scene_id == scene.id
        ]
        for event in events:
            if event.slot_id is None and len(slots) != 1:
                raise RenderError(
                    "landmark needs an explicit slot when the scene has multiple sprite slots"
                )
            if event.slot_id is not None and event.slot_id not in {s.id for s in slots}:
                raise RenderError("landmark references an unknown scheduled sprite slot")
        blank = self.root / f"transparent-{width}-{height}.png"
        if not blank.exists():
            Image.new("RGBA", (width, height), (0, 0, 0, 0)).save(blank)
        blank_input, base = self.input(blank), self.label()
        self.filter(f"[{blank_input}]format=rgba,setparams=alpha_mode=straight[{base}]")
        # On the pinned FFmpeg build, overlay position n is one-based. The
        # generic enable expression and crop n are zero-based (verified in media tests).
        distance = distance_expression(self.timeline, scene.id, f"(n-1+{start})")
        for event in events:
            if (
                (event.slot_id is not None and event.slot_id != slot.id)
                or event.end_frame <= start
                or event.start_frame >= end
            ):
                continue
            layer, _ = self.still(event.asset)
            asset = self.registry.get(event.asset, "asset")
            anchor = self.registry.get(scene.template, "scene_template").anchors.get(slot.anchor)
            origin_x, origin_y = (anchor.x, anchor.y) if anchor else (0, 0)
            if asset.compatibility.anchor:
                origin_x -= asset.compatibility.anchor.x
                origin_y -= asset.compatibility.anchor.y
            if asset.compatibility.crop:
                origin_x += asset.compatibility.crop.x
                origin_y += asset.compatibility.crop.y
            x = (
                f"floor({number(event.world_x + origin_x)}-"
                f"{number(slot.depth_factor)}*({distance})+0.0000001)"
            )
            enable = (
                f"gte(n,{max(start, event.start_frame) - start})*"
                f"lt(n,{min(end, event.end_frame) - start})"
            )
            base = self.overlay(base, layer, x=x, y=round(origin_y), enable=enable)
        return self.mask_and_opacity(base, slot, (width, height))

    def scene(self, scene, start, end):
        template = self.registry.get(scene.template, "scene_template")
        validate_effects(scene, template, self.timeline, self.registry.get)
        width, height = template.design_canvas.width, template.design_canvas.height
        if any(
            isinstance(event, LandmarkEvent) and event.scene_id == scene.id
            for event in self.registry.snapshot.schedule
        ) and not any(slot.kind == "scheduled_sprite" for slot in template.slots):
            raise RenderError("scene has landmark events but no scheduled sprite slot")
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
            elif slot.kind == "tile_strip":
                base = self.overlay(base, self.tile(scene, slot, start, width, height))
            elif slot.kind == "scheduled_sprite":
                base = self.overlay(base, self.landmarks(scene, slot, start, end, width, height))
            elif slot.kind == "effect":
                base = self.overlay(base, self.effect(scene, slot, start, end, width, height))
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
                raise RenderError(f"unsupported slot capability: {slot.kind}")
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

    def effect(self, scene, slot, start, end, width, height):
        spec = slot.effect
        if spec.kind == "tint":
            path = self.root / f"tint-{self.counter}.png"
            Image.new("RGBA", (width, height), (*spec.color, 255)).save(path)
            raw, layer = self.input(path), self.label()
            self.filter(f"[{raw}]format=rgba,setparams=alpha_mode=straight[{layer}]")
        else:
            ref = scene.slot_assignments.get(slot.id, slot.asset)
            asset = self.registry.get(ref, "asset")
            if spec.loop:
                folder = self.root / f"effect-{self.counter}"
                folder.mkdir()
                for local, frame in enumerate(range(start, end)):
                    checkpoint()
                    source = loop_frame(frame, scene.initial_state.weather_phase_frame, spec.loop)
                    prepared = self.normalizer.prepare(asset, source)
                    os.link(prepared, folder / f"{local:06}.png")
                raw, layer = self.input(folder / "%06d.png", loop=False), self.label()
                self.filter(f"[{raw}]format=rgba,setparams=alpha_mode=straight[{layer}]")
            else:
                layer, _ = self.still(ref)
        color, alpha_source, alpha, varied = [self.label() for _ in range(4)]
        self.filter(f"[{layer}]split[{color}][{alpha_source}]")
        opacity = self.effect_opacity(scene, spec, start, end, alpha)
        self.filter(f"[{alpha_source}]alphaextract,{opacity}[{alpha}]")
        self.filter(
            f"[{color}][{alpha}]alphamerge,format=rgba,setparams=alpha_mode=straight[{varied}]"
        )
        return self.mask_and_opacity(varied, slot, (width, height))

    def effect_opacity(self, scene, spec, start, end, name):
        if Fraction(self.rate.num, self.rate.den) > 1000:
            # sendcmd has microsecond timestamps. Preserve the existing exact
            # frame-expression path for unusually high custom frame rates.
            strength = value_expression(
                self.timeline,
                scene.id,
                spec.strength_target,
                f"(N+{start})",
                default=spec.default_strength,
            )
            return f"geq=lum='lum(X,Y)*({strength})'"
        values = [
            self.timeline.value_at(
                scene.id, spec.strength_target, frame, default=spec.default_strength
            )
            for frame in range(start, end)
        ]
        target = f"lut@opacity_{name}"
        commands = []
        for local, (previous, value) in enumerate(zip(values, values[1:], strict=False), 1):
            if value != previous:
                # Schedule between the previous/current frames so microsecond
                # rounding cannot delay a command at fractional frame rates.
                stamp = Fraction((2 * local - 1) * self.rate.den, 2 * self.rate.num)
                commands.append(f"{float(stamp):.9f} {target} c0 val*{number(value)}")
        lut = f"{target}=c0='val*{number(values[0])}'"
        return (f"sendcmd=c='{';'.join(commands)}'," if commands else "") + lut

    def build(self, start, end, *, video):
        parts = []
        scenes = self.registry.snapshot.episode.scenes
        boundaries = {start, end}
        for scene in scenes:
            boundaries.update(n for n in (scene.start_frame, scene.end_frame) if start < n < end)
        boundaries = sorted(boundaries)
        for left, right in zip(boundaries, boundaries[1:], strict=False):
            active = [scene for scene in scenes if scene.start_frame <= left < scene.end_frame]
            layers = [self.scene(scene, left, right) for scene in active]
            if len(layers) == 1:
                parts.append(layers[0])
            elif len(layers) == 2:
                incoming = active[1]
                progress = (
                    f"min(1,max(0,(T*{self.rate.num}/{self.rate.den}+{left}-"
                    f"{incoming.start_frame})/{incoming.transition_in.overlap_frames - 1}))"
                )
                out = self.label()
                self.filter(
                    f"[{layers[0]}][{layers[1]}]blend=all_expr='A*(1-({progress}))+B*({progress})':"
                    f"shortest=1[{out}]"
                )
                parts.append(out)
            else:
                raise RenderError("scene coverage needs one scene or a declared two-scene overlap")
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
                "-show_format",
                "-of",
                "json",
                str(path),
            ],
            timeout=300,
        )
    )
    streams = probe.get("streams", [])
    videos = [stream for stream in streams if stream.get("codec_type") == "video"]
    if len(videos) != 1 or len(streams) != (2 if profile.audio_codec else 1):
        raise RenderError("render has unexpected video/audio streams")
    stream = videos[0]
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
    duration = Fraction(int(stream["duration_ts"])) * Fraction(stream["time_base"])
    intended = Fraction(frames * profile.fps.den, profile.fps.num)
    container_duration = Fraction(probe["format"]["duration"])
    if (
        # MP4 edit-list/movie timescales may round duration more coarsely than
        # video ticks. Frame count and every PTS are checked exactly below;
        # duration metadata must remain within the one-frame delivery bound.
        abs(duration - intended) > Fraction(profile.fps.den, profile.fps.num)
        or abs(container_duration - intended) > Fraction(profile.fps.den, profile.fps.num)
        or abs(Fraction(stream.get("start_time", "0"))) > Fraction(stream["time_base"])
    ):
        raise RenderError(
            f"encoded video/container duration differs from its frame schedule: "
            f"video={duration}, container={container_duration}, intended={intended}, "
            f"start={stream.get('start_time')}"
        )
    if stream.get("profile") != "High" or stream.get("field_order") != "progressive":
        raise RenderError("export requires progressive H.264 High Profile")
    if stream.get("sample_aspect_ratio") != "1:1":
        raise RenderError("export requires square pixels")
    layout = verify_fast_start(path)
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
    return VideoVerification(
        canvas=profile.canvas,
        fps=profile.fps,
        frame_count=frames,
        level=stream["level"],
        duration_seconds=float(duration),
        container_duration_seconds=float(container_duration),
        bit_rate=int(stream["bit_rate"]) if stream.get("bit_rate") else None,
        mp4=layout,
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
            "tile_strip",
            "scheduled_sprite",
            "lighting",
            "rain",
            "reflection",
            "matched_overlap",
            "single_character_overlap",
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
            or profile.audio_codec not in {None, "aac"}
        ):
            raise RenderError(
                "backend requires matching fps and H.264/YUV420P MP4 with optional AAC audio"
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
        if profile:
            require_encoder(capabilities, profile)
        registry = FrozenRegistry(self.assets, snapshot)
        validate_transitions(snapshot.episode, snapshot.schedule, registry.get)
        with tempfile.TemporaryDirectory(prefix=".tabi-render-", dir=output.parent) as scratch:
            root = Path(scratch)
            builder = GraphBuilder(registry, root, canvas)
            graph = builder.build(start, end, video=profile is not None)
            graph_path = root / "graph.txt"
            graph_path.write_text(graph)
            temporary = root / ("video-only.mp4" if profile else "frame.png")
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
                args.extend(video_arguments(profile))
            else:
                args.extend(["-update", "1", "-c:v", "png"])
            args.append(str(temporary))
            began = time.monotonic()
            run_tool(args, timeout=600)
            audio_mix, audio_verification = None, None
            if profile and profile.audio_codec:
                audio_path = root / "continuous.wav"
                audio_mix = AudioMixer(self.assets, self.settings).render(
                    snapshot,
                    audio_path,
                    start_sample=snapshot.episode.fps.sample_at(start),
                    end_sample=snapshot.episode.fps.sample_at(end),
                    gain_db=profile.audio_gain_db,
                )
                if audio_mix.over_full_scale_samples:
                    raise RenderError(
                        "mix exceeds full scale; reduce explicit audio gain before encoding"
                    )
                muxed = root / "muxed.mp4"
                audio_verification = mux_aac(
                    self.settings,
                    temporary,
                    audio_path,
                    muxed,
                    expected_samples=audio_mix.sample_count,
                    scratch=root,
                    bitrate=profile.audio_bitrate,
                )
                temporary = muxed
                audio_mix = audio_mix.model_copy(update={"output": None})
            elapsed = time.monotonic() - began
            if profile:
                verified_video = verify_video(self.settings, temporary, profile, end - start)
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
                normalized_cache_hits=builder.normalizer.cache_hits,
                video_verification=verified_video if profile else None,
                warnings=sorted(builder.normalizer.warnings),
                audio_mix=audio_mix,
                audio_verification=audio_verification,
            )
            with temporary.open("rb") as source:
                os.fsync(source.fileno())
            checkpoint(force=True)
            os.link(temporary, output)
            descriptor = os.open(output.parent, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
            return report
