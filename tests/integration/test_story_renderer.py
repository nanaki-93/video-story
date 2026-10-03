import math
import os
from fractions import Fraction
from pathlib import Path

import numpy as np
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
from tabi.core.render.ffmpeg import FFmpegRenderer
from tabi.core.timeline.compiler import ActionCompiler

pytestmark = pytest.mark.media


def reference_story(service, frame, *, single=False):
    """Independent composition for the authored fixture near its overlap."""

    def image(name, index=0):
        asset = service.load(AssetRef(id=f"fixture.{name}", version="1.0"))
        with Image.open(service.resolve(asset.files[index].location)) as source:
            return source.convert("RGBA")

    distance = 180 + max(0, frame - 150) * 4
    mask = image("window").convert("L")
    scenes = []
    for incoming in (False, True):
        result = image("cabin")
        names = ("near", "far", "near") if incoming else ("far", "mid", "near")
        for name, depth in zip(names, [Fraction(1, 5), Fraction(11, 20), 1], strict=True):
            crop = math.floor(distance * depth % 640)
            layer = image(name).crop((crop, 0, crop + 640, 360))
            layer.putalpha(ImageChops.multiply(layer.getchannel("A"), mask))
            result = Image.alpha_composite(result, layer)
        if not (single and incoming):
            result.alpha_composite(image("idle", frame % 12), (322, 202))
        scenes.append(Image.alpha_composite(result, image("foreground")).convert("RGB"))
    return Image.blend(scenes[0], scenes[1], min(1, max(0, (frame - 144) / 35)))


@pytest.mark.parametrize("single", [False, True])
def test_actual_story_overlap_endpoints_and_split_phase(tmp_path, single):
    root = tmp_path / "Story 東京"
    generate_fixtures(root, profile="story")
    service = AssetService(ProjectStore(root))
    episode = service.store.read("episodes/episode.synthetic.json")
    if single:
        template = service.store.read("registry/templates/scene.synthetic.train/1.0.json")
        data = template.model_dump(mode="json")
        data.update(id="scene.environment", channels=[])
        data["slots"] = [s for s in data["slots"] if s["kind"] != "character"]
        service.store.save_draft(SceneTemplate.model_validate(data), expected_revision=None)
        data = episode.model_dump(mode="json")
        data["scenes"][1]["template"]["id"] = "scene.environment"
        data["actions"] = [a for a in data["actions"] if a["scene_id"] != "city"]
        for transition in [data["scenes"][0]["transition_out"], data["scenes"][1]["transition_in"]]:
            transition.update(character_policy="single_visible", match_action=None)
        episode = Episode.model_validate(data)
    snapshot = ActionCompiler(service, purpose="synthetic_test").compile(episode)
    settings = load_settings(None, env=os.environ, cwd=Path.cwd(), home=Path.home())
    renderer = FFmpegRenderer(service, settings)
    for frame in [143, 144, 145, 162, 178, 179, 180]:
        output = tmp_path / f"frame-{frame}.png"
        renderer.frame(snapshot, frame, output)
        with Image.open(output) as actual:
            reference = reference_story(service, frame, single=single)
            diff = ImageChops.difference(
                actual.crop((0, 0, 640, 332)), reference.crop((0, 0, 640, 332))
            )
            assert max(high for _, high in diff.getextrema()) <= 3, frame
    profile = OutputProfile(
        id="story.proxy",
        canvas=Canvas(width=640, height=360),
        fps=episode.fps,
        container="mp4",
        video_codec="libx264",
        pixel_format="yuv420p",
        color_space="bt709",
    )
    arrays = []
    for start, end in [(140, 186), (161, 182)]:
        output = tmp_path / f"range-{start}.mp4"
        report = renderer.clip(snapshot, start, end, output, profile)
        assert report.frame_count == end - start and report.full_decode_passed
        raw = run_tool(
            [
                settings.ffmpeg,
                "-v",
                "error",
                "-i",
                str(output),
                "-vf",
                "scale=in_color_matrix=bt709:in_range=tv:out_range=pc,format=rgb24",
                "-f",
                "rawvideo",
                "-",
            ],
            max_bytes=640 * 360 * 3 * (end - start),
        )
        arrays.append(np.frombuffer(raw, dtype=np.uint8).reshape(end - start, 360, 640, 3))
    diff = np.abs(arrays[0][21:42].astype(np.int16) - arrays[1].astype(np.int16))
    assert np.quantile(diff, 0.999) <= 10
    for local, frame in enumerate(range(161, 182)):
        reference = tmp_path / f"reference-{frame}.png"
        reference_story(service, frame, single=single).save(reference)
        # Compare the encoded pixels after the documented BT.709 / 4:2:0 interchange.
        # RGB-only edge comparisons would confuse chroma subsampling with a phase error.
        raw = run_tool(
            [
                settings.ffmpeg,
                "-v",
                "error",
                "-i",
                str(reference),
                "-vf",
                "scale=in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p,"
                "scale=in_range=tv:out_range=pc:in_color_matrix=bt709,format=rgb24",
                "-frames:v",
                "1",
                "-f",
                "rawvideo",
                "-",
            ],
            max_bytes=640 * 360 * 3,
        )
        expected = np.frombuffer(raw, dtype=np.uint8).reshape(360, 640, 3).astype(np.int16)
        diff = np.abs(arrays[1][local, :332].astype(np.int16) - expected[:332])
        assert np.quantile(diff, 0.999) <= 15, frame
