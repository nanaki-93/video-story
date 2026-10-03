import math
import os
from fractions import Fraction
from pathlib import Path

import pytest
from PIL import Image, ImageChops

from tabi.core.assets import AssetService
from tabi.core.config import load_settings
from tabi.core.fixtures import generate_fixtures
from tabi.core.models import Episode, SceneTemplate
from tabi.core.models.base import AssetRef, Canvas
from tabi.core.models.production import OutputProfile
from tabi.core.persistence import ProjectStore
from tabi.core.process import run_tool
from tabi.core.render.backend import RenderError
from tabi.core.render.ffmpeg import FFmpegRenderer
from tabi.core.timeline import Timeline
from tabi.core.timeline.compiler import ActionCompiler, CompileError

pytestmark = pytest.mark.media


def motion_fixture(root, *, acceleration=False):
    generate_fixtures(root)
    service = AssetService(ProjectStore(root))
    episode = service.store.read("episodes/episode.synthetic.json")
    if acceleration:
        data = episode.model_dump(mode="json")
        data["scenes"][0]["final_state"] = None
        data["curves"][0].update(
            interpolation="linear",
            keys=[
                {"frame": n, "value": v}
                for n, v in [(0, 0), (60, 60), (120, 0), (180, 0), (240, 120), (300, 120)]
            ],
        )
        episode = Episode.model_validate(data)
    snapshot = ActionCompiler(service, purpose="synthetic_test").compile(episode)
    settings = load_settings(None, env=os.environ, cwd=Path.cwd(), home=Path.home())
    return service, snapshot, settings


def reference_motion(service, snapshot, frame):
    def image(name, index=0):
        asset = service.load(AssetRef(id=f"fixture.{name}", version="1.0"))
        with Image.open(service.resolve(asset.files[index].location)) as source:
            return source.convert("RGBA")

    distance = Timeline(snapshot.episode).travel_at("train", frame)
    result = image("cabin")
    mask = image("window").convert("L")
    for name, depth in [("far", Fraction(1, 5)), ("mid", Fraction(11, 20)), ("near", Fraction(1))]:
        crop = math.floor((distance * depth) % 640)
        layer = image(name).crop((crop, 0, crop + 640, 360))
        layer.putalpha(ImageChops.multiply(layer.getchannel("A"), mask))
        result = Image.alpha_composite(result, layer)
    landmark = Image.new("RGBA", (640, 360))
    landmark.alpha_composite(image("landmark"), (math.floor(620 - distance), 150))
    landmark.putalpha(ImageChops.multiply(landmark.getchannel("A"), mask))
    result = Image.alpha_composite(result, landmark)
    if frame < 84:
        name, source = "idle", frame % 12
    elif frame < 90:
        name, source = "entry", frame - 84
    elif frame < 210:
        name, source = "observe", (frame - 90) % 12
    elif frame < 216:
        name, source = "exit", frame - 210
    else:
        name, source = "idle", (frame - 216) % 12
    result.alpha_composite(image(name, source), (322, 202))
    for start in [36, 270]:
        if start <= frame < start + 6:
            result.alpha_composite(image("blink", frame - start), (322, 202))
    return Image.alpha_composite(result, image("foreground")).convert("RGB")


@pytest.mark.parametrize("acceleration", [False, True])
def test_actual_motion_pixels_at_stop_restart_and_tile_wrap(tmp_path, acceleration):
    service, snapshot, settings = motion_fixture(
        tmp_path / "Motion 東京", acceleration=acceleration
    )
    renderer = FFmpegRenderer(service, settings)
    for frame in [0, 89, 90, 149, 150, 151, 209, 240, 264, 265, 270, 299]:
        output = tmp_path / f"frame-{frame}.png"
        renderer.frame(snapshot, frame, output)
        with Image.open(output) as actual:
            expected = reference_motion(service, snapshot, frame)
            error = ImageChops.difference(
                actual.crop((0, 0, 640, 332)), expected.crop((0, 0, 640, 332))
            )
            assert max(high for low, high in error.getextrema()) <= 2, frame


def test_full_clip_landmark_passes_once_and_range_restart_keeps_phase(tmp_path):
    service, snapshot, settings = motion_fixture(tmp_path / "full motion")
    renderer = FFmpegRenderer(service, settings)
    profile = OutputProfile(
        id="motion.proxy",
        canvas=Canvas(width=640, height=360),
        fps=snapshot.episode.fps,
        container="mp4",
        video_codec="libx264",
        pixel_format="yuv420p",
        color_space="bt709",
    )
    movie = tmp_path / "motion.mp4"
    renderer.clip(snapshot, 0, 300, movie, profile)
    # A cropped scan region around the landmark's red disk excludes the character.
    raw = run_tool(
        [
            settings.ffmpeg,
            "-v",
            "error",
            "-i",
            str(movie),
            "-vf",
            "crop=580:50:30:154,format=rgb24",
            "-f",
            "rawvideo",
            "-",
        ],
        max_bytes=580 * 50 * 3 * 300,
    )
    visible = []
    for frame in range(300):
        pixels = raw[frame * 580 * 50 * 3 : (frame + 1) * 580 * 50 * 3]
        visible.append(
            any(
                pixels[i] > 195 and pixels[i + 1] < 130 and pixels[i + 2] < 145
                for i in range(0, len(pixels), 3)
            )
        )
    indices = [n for n, present in enumerate(visible) if present]
    assert indices and indices == list(range(indices[0], indices[-1] + 1))
    assert 5 <= indices[0] <= 20 and 250 <= indices[-1] <= 270
    assert not any(visible[280:])
    # Global crop offset must not reset in a render beginning at the restart.
    cropped = tmp_path / "restart.mp4"
    renderer.clip(snapshot, 149, 154, cropped, profile)
    raw = run_tool(
        [
            settings.ffmpeg,
            "-v",
            "error",
            "-i",
            str(cropped),
            "-vf",
            "scale=in_color_matrix=bt709:in_range=tv:out_range=pc,format=rgb24",
            "-f",
            "rawvideo",
            "-",
        ],
        max_bytes=640 * 360 * 3 * 5,
    )
    for local in range(5):
        actual = Image.frombytes(
            "RGB", (640, 360), raw[local * 640 * 360 * 3 : (local + 1) * 640 * 360 * 3]
        )
        expected = reference_motion(service, snapshot, 149 + local)
        for x, y in [(80, 80), (210, 190), (550, 230), (600, 100)]:
            assert (
                max(
                    abs(a - b)
                    for a, b in zip(actual.getpixel((x, y)), expected.getpixel((x, y)), strict=True)
                )
                <= 15
            )


def test_wrong_period_and_missing_sprite_slot_fail(tmp_path):
    service, snapshot, settings = motion_fixture(tmp_path / "bad tile")
    template = service.store.read("registry/templates/scene.synthetic.train/1.0.json")
    data = template.model_dump(mode="json")
    data["slots"][1]["tile_period"] = 639
    service.store.save_draft(
        SceneTemplate.model_validate(data), expected_revision=template.revision
    )
    snapshot = ActionCompiler(service, purpose="synthetic_test").compile(snapshot.episode)
    output = tmp_path / "bad.png"
    with pytest.raises(RenderError, match="do not repeat"):
        FFmpegRenderer(service, settings).frame(snapshot, 10, output)
    assert not output.exists()
    current = service.store.read("registry/templates/scene.synthetic.train/1.0.json")
    data = current.model_dump(mode="json")
    data["slots"] = [slot for slot in data["slots"] if slot["kind"] != "scheduled_sprite"]
    service.store.save_draft(SceneTemplate.model_validate(data), expected_revision=current.revision)
    with pytest.raises(CompileError, match="sprite slot"):
        ActionCompiler(service, purpose="synthetic_test").compile(snapshot.episode)
