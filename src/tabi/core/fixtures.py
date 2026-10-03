"""Deterministic geometric development project with portable, hashed media."""

import os
import sys
import tempfile
import wave
from array import array
from pathlib import Path

from PIL import Image, ImageDraw

from .documents import validate_data
from .models import FixtureManifest
from .models.base import HashedFile, MediaPath, canonical_bytes
from .persistence import ProjectStore, StorageError
from .render.synthetic import label, png
from .toolchain import file_hash

CANVAS = {"width": 640, "height": 360}
FPS = {"num": 30, "den": 1}
VERSION = "1.0"


def ref(name: str) -> dict:
    return {"id": name, "version": VERSION}


def hashed(root: Path, path: Path) -> HashedFile:
    return HashedFile(
        location=MediaPath(path=path.relative_to(root).as_posix()),
        sha256=file_hash(path),
        size_bytes=path.stat().st_size,
    )


def save_image(path: Path, image: Image.Image) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    png(path, image.width, image.height, image.tobytes(), {"L": 1, "RGB": 3, "RGBA": 4}[image.mode])


def body_frame(shift: int, breath: int = 0) -> Image.Image:
    image = Image.new("RGBA", (96, 96), (80, 180, 210, 0))
    draw = ImageDraw.Draw(image)
    draw.rectangle((26, 46 - breath, 70, 89), fill=(72, 164, 188, 255))
    draw.rectangle((28 + shift, 14, 64 + shift, 48), fill=(244, 184, 120, 255))
    draw.rectangle((36 + shift, 27, 40 + shift, 30), fill=(32, 48, 64, 255))
    draw.rectangle((52 + shift, 27, 56 + shift, 30), fill=(32, 48, 64, 255))
    draw.rectangle((20, 86, 43, 91), fill=(120, 80, 152, 255))
    draw.rectangle((55, 86, 78, 91), fill=(120, 80, 152, 255))
    return image


def write_wav(path: Path, count: int, *, silence: bool = False) -> None:
    samples = array("h")
    for n in range(count):
        # Integer triangle at 500 Hz: repeatable without platform libm rounding.
        position = n % 96
        value = (position if position < 48 else 96 - position) * 160 - 3840
        value = 0 if silence else value * min(480, n, count - 1 - n) // 480
        samples.extend((value, value))
    if sys.byteorder != "little":
        samples.byteswap()
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as stream:
        stream.setnchannels(2)
        stream.setsampwidth(2)
        stream.setframerate(48000)
        stream.writeframes(samples.tobytes())


def _populate(root: Path) -> FixtureManifest:
    root.mkdir()
    store = ProjectStore(root)
    project = validate_data(
        {
            "schema_version": VERSION,
            "document_type": "project",
            "id": "fixture-project-v1",
            "title": "SYNTHETIC development project — not Tabi artwork",
            "episode_ids": ["episode.synthetic"],
            # Fixed synthetic metadata, not a claim about a real asset's creation date.
            "created_at": "2000-01-01T00:00:00Z",
            "updated_at": "2000-01-01T00:00:00Z",
        }
    )
    store.save_draft(project, expected_revision=None)

    def register(
        name, images=None, *, kind="still", audio_count=None, silence=False, channels=None
    ):
        paths = []
        if audio_count is not None:
            path = root / "audio" / f"{name}.wav"
            write_wav(path, audio_count, silence=silence)
            paths.append(path)
            probe = {
                "sample_rate": 48000,
                "channels": 2,
                "duration_samples": audio_count,
                "codec": "pcm_s16le",
            }
        else:
            for n, image in enumerate(images):
                path = (
                    root / "assets" / name / (f"{n:06}.png" if kind == "sequence" else "image.png")
                )
                save_image(path, image)
                paths.append(path)
            image = images[0]
            probe = {
                "canvas": {"width": image.width, "height": image.height},
                "codec": "png",
                "pixel_format": image.mode.lower(),
                "color_space": "grayscale" if kind == "mask" else "srgb",
                "alpha_mode": "straight" if image.mode == "RGBA" else "none",
            }
            if kind == "sequence":
                probe.update(fps=FPS, frame_count=len(images))
        asset = validate_data(
            {
                "schema_version": VERSION,
                "document_type": "asset",
                **ref(name),
                "kind": kind,
                "source": {"path": paths[0].relative_to(root).as_posix()},
                "files": [hashed(root, path).model_dump(mode="json") for path in paths],
                "probe": probe,
                "compatibility": {"cameras": ["fixture.camera"], "channels": channels or []},
                "provenance": {
                    "origin": "synthetic",
                    "creator": "tabi-fixtures-v1",
                    "commercial_use": "pending",
                    "notes": "Owned geometric test input. Not Tabi artwork or approved music; "
                    "not for publication.",
                },
            }
        )
        store.save_draft(asset, expected_revision=None)

    pixels = bytearray(bytes((32, 48, 64)) * 640 * 360)
    label(pixels, 640, "SYNTHETIC TEST", 20, 16, 2)
    label(pixels, 640, "NOT FOR PUBLICATION", 20, 336, 2)
    register("fixture.cabin", [Image.frombytes("RGB", (640, 360), bytes(pixels))])
    mask = Image.new("L", (640, 360))
    ImageDraw.Draw(mask).rectangle((30, 60, 609, 269), fill=255)
    register("fixture.window", [mask], kind="mask")
    foreground = Image.new("RGBA", (640, 360))
    ImageDraw.Draw(foreground).rectangle((280, 276, 450, 310), fill=(120, 80, 152, 255))
    register("fixture.foreground", [foreground])
    for layer, color, top in [
        ("far", (174, 210, 224, 255), 0),
        ("mid", (112, 152, 136, 255), 145),
        ("near", (76, 100, 132, 255), 215),
    ]:
        tile = Image.new("RGBA", (640, 360), (0, 0, 0, 0))
        draw = ImageDraw.Draw(tile)
        for n in range(8):
            draw.rectangle((n * 80, top + (n % 3) * 12, n * 80 + 79, 359), fill=color)
            draw.rectangle(
                (n * 80 + 12, top + 30, n * 80 + 50, top + 52), fill=(228, 198, 144, 255)
            )
        rgb = bytearray(tile.convert("RGB").tobytes())
        for n in range(8):
            label(rgb, 640, str(n), n * 80 + 26, min(top + 65, 330), 2)
        numbered = Image.frombytes("RGB", tile.size, bytes(rgb)).convert("RGBA")
        numbered.putalpha(tile.getchannel("A"))
        strip = Image.new("RGBA", (1280, 360))
        strip.paste(numbered, (0, 0))
        strip.paste(numbered, (640, 0))
        register(f"fixture.{layer}", [strip])
    landmark = Image.new("RGBA", (64, 96))
    ImageDraw.Draw(landmark).ellipse((4, 4, 59, 59), fill=(248, 88, 96, 255))
    ImageDraw.Draw(landmark).rectangle((27, 58, 36, 95), fill=(240, 224, 176, 255))
    register("fixture.landmark", [landmark])
    breathing = [0, 1, 1, 2, 2, 1, 1, 0, -1, -1, 0, 0]
    register(
        "fixture.idle", [body_frame(0, n) for n in breathing], kind="sequence", channels=["body"]
    )
    register(
        "fixture.observe",
        [body_frame(10, n) for n in breathing],
        kind="sequence",
        channels=["body"],
    )
    register(
        "fixture.entry",
        [body_frame(n) for n in (0, 2, 4, 6, 8, 10)],
        kind="sequence",
        channels=["body"],
    )
    register(
        "fixture.exit",
        [body_frame(n) for n in (10, 8, 6, 4, 2, 0)],
        kind="sequence",
        channels=["body"],
    )
    blinks = []
    for frame in range(6):
        blink = Image.new("RGBA", (96, 96))
        if frame in (1, 2, 3, 4):
            draw = ImageDraw.Draw(blink)
            for x in (36, 52):
                draw.rectangle((x, 27, x + 4, 30), fill=(244, 184, 120, 255))
                draw.line((x, 29, x + 4, 29), fill=(32, 48, 64, 255))
        blinks.append(blink)
    register("fixture.blink", blinks, kind="sequence", channels=["face"])
    register("fixture.tone", kind="audio", audio_count=480000)
    register("fixture.silence", kind="audio", audio_count=48000, silence=True)
    template = validate_data(
        {
            "schema_version": VERSION,
            "document_type": "scene_template",
            **ref("scene.synthetic.train"),
            "camera_id": "fixture.camera",
            "design_canvas": CANVAS,
            "capabilities": ["travel", "landmarks", "body", "face"],
            "channels": ["body", "face"],
            "anchors": {"seated": {"x": 370, "y": 294}},
            "mask_semantics": "white_visible_black_hidden",
            "parameter_limits": {"travel_speed": {"minimum": 0, "maximum": 180}},
            "slots": [
                {"id": "cabin", "z": 0, "kind": "still", "asset": ref("fixture.cabin")},
                *[
                    {
                        "id": layer,
                        "z": n + 1,
                        "kind": "tile_strip",
                        "asset": ref(f"fixture.{layer}"),
                        "mask": ref("fixture.window"),
                        "tile_period": 640,
                        "depth_factor": depth,
                    }
                    for n, (layer, depth) in enumerate([("far", 0.2), ("mid", 0.55), ("near", 1.0)])
                ],
                {
                    "id": "landmarks",
                    "z": 4,
                    "kind": "scheduled_sprite",
                    "mask": ref("fixture.window"),
                },
                {"id": "actor", "z": 5, "kind": "character", "anchor": "seated"},
                {"id": "foreground", "z": 6, "kind": "still", "asset": ref("fixture.foreground")},
            ],
        }
    )
    store.save_draft(template, expected_revision=None)
    actions = []
    for name, start, end, count, loop in [
        ("idle", "idle", "idle", 12, True),
        ("entry", "idle", "observing", 6, False),
        ("observe", "observing", "observing", 12, True),
        ("exit", "observing", "idle", 6, False),
        ("blink", "eyes-open", "eyes-open", 6, False),
    ]:
        channel = "face" if name == "blink" else "body"
        actions.append(
            {
                **ref(f"fixture.{name}"),
                "channel": channel,
                "start_pose": start,
                "end_pose": end,
                "frame_count": count,
                "clip": ref(f"fixture.{name}"),
                "kind": "loop" if loop else "one_shot",
                "loop": {"start_frame": 0, "end_frame": count} if loop else None,
                "occupies_channels": [channel],
                "compatible_body_poses": ["idle"] if name == "blink" else [],
            }
        )
    pack = validate_data(
        {
            "schema_version": VERSION,
            "document_type": "action_pack",
            **ref("pack.synthetic"),
            "camera_id": "fixture.camera",
            "template": ref(template.id),
            "canvas": {"width": 96, "height": 96},
            "anchor": {"x": 48, "y": 92},
            "fps": FPS,
            "alpha_mode": "straight",
            "actions": actions,
        }
    )
    store.save_draft(pack, expected_revision=None)
    requests = []
    for name, start, end in [
        ("idle", 0, 84),
        ("entry", 84, 90),
        ("observe", 90, 210),
        ("exit", 210, 216),
        ("idle", 216, 300),
        ("blink", 36, 42),
        ("blink", 270, 276),
    ]:
        requests.append(
            {
                "id": f"{name}-{start}",
                "scene_id": "train",
                "pack": ref(pack.id),
                "action_id": f"fixture.{name}",
                "version": VERSION,
                "channel": "face" if name == "blink" else "body",
                "start_frame": start,
                "end_frame": end,
                "repeat": "loop_to_fill" if name in {"idle", "observe"} else "once",
            }
        )
    episode = validate_data(
        {
            "schema_version": VERSION,
            "document_type": "episode",
            "id": "episode.synthetic",
            "title": "SYNTHETIC fixture story",
            "format": "story",
            "fps": FPS,
            "canvas": CANVAS,
            "duration_frames": 300,
            "seed": 12345,
            "scenes": [
                {
                    "id": "train",
                    "template": ref(template.id),
                    "start_frame": 0,
                    "end_frame": 300,
                    "anchor": "seated",
                    "initial_state": {"body_pose": "idle"},
                    "final_state": {"body_pose": "idle"},
                }
            ],
            "actions": requests,
            "curves": [
                {
                    "scope": "train",
                    "target": "travel_speed",
                    "unit": "design_px_per_second",
                    "interpolation": "constant",
                    "limits": {"minimum": 0, "maximum": 180},
                    "keys": [
                        {"frame": 0, "value": 60},
                        {"frame": 90, "value": 0},
                        {"frame": 150, "value": 120},
                        {"frame": 300, "value": 120},
                    ],
                }
            ],
            "events": [
                {
                    "type": "landmark",
                    "id": "landmark.once",
                    "scene_id": "train",
                    "asset": ref("fixture.landmark"),
                    "start_frame": 0,
                    "end_frame": 300,
                    "world_x": 620,
                }
            ],
            "tracks": [
                {
                    "id": "tone",
                    "asset": ref("fixture.tone"),
                    "start_sample": 0,
                    "trim_start_sample": 0,
                    "trim_end_sample": 480000,
                    "fade_in_samples": 480,
                    "fade_out_samples": 480,
                }
            ],
            "notes": "Synthetic placeholders only. Not an approved Tabi scene or music release.",
        }
    )
    store.save_draft(episode, expected_revision=None)
    files = [
        hashed(root, path)
        for path in sorted(root.rglob("*"))
        if path.is_file() and path.name != ".tabi.lock"
    ]
    manifest = FixtureManifest(
        schema_version=VERSION, generator_sha256=file_hash(Path(__file__)), files=files
    )
    (root / "fixtures.json").write_bytes(canonical_bytes(manifest))
    return manifest


def generate_fixtures(output: Path) -> FixtureManifest:
    """Publish a new fixture project only; never merge into or replace an existing one."""
    output = output.expanduser().resolve()
    if output.exists():
        raise StorageError("fixture output already exists; choose a new directory")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".tabi-fixtures-", dir=output.parent) as temporary:
        staging = Path(temporary) / "project"
        manifest = _populate(staging)
        for entry in manifest.files:
            if file_hash(staging / entry.location.path) != entry.sha256:
                raise StorageError("fixture hash verification failed")
        output.mkdir(mode=0o700)  # Exclusive claim; a competing writer must fail.
        try:
            os.replace(staging, output)
        except BaseException:
            output.rmdir()  # Only this operation's still-empty directory.
            raise
    return manifest
