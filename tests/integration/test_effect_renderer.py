import os
from pathlib import Path

import numpy as np
import pytest
from PIL import Image, ImageChops
from test_motion_renderer import reference_motion

from tabi.core.assets import AssetService
from tabi.core.config import load_settings
from tabi.core.fixtures import generate_fixtures
from tabi.core.models.base import Canvas
from tabi.core.models.production import OutputProfile
from tabi.core.persistence import ProjectStore
from tabi.core.process import run_tool
from tabi.core.render.ffmpeg import FFmpegRenderer
from tabi.core.timeline.compiler import ActionCompiler

pytestmark = pytest.mark.media


def effect_fixture(root):
    generate_fixtures(root, profile="effects")
    assets = AssetService(ProjectStore(root))
    snapshot = ActionCompiler(assets, purpose="synthetic_test").compile(
        assets.store.read("episodes/episode.synthetic.json")
    )
    settings = load_settings(None, env=os.environ, cwd=Path.cwd(), home=Path.home())
    return assets, snapshot, settings


def test_effect_stills_match_independent_mask_strength_and_layer_order(tmp_path):
    assets, snapshot, settings = effect_fixture(tmp_path / "effect stills")
    renderer = FFmpegRenderer(assets, settings)
    for frame in [0, 59, 60, 61, 119, 120, 149, 150, 151, 209, 210, 211, 299]:
        path = tmp_path / f"effect-{frame}.png"
        renderer.frame(snapshot, frame, path)
        with Image.open(path) as actual:
            expected = reference_motion(assets, snapshot, frame, effects=True)
            difference = ImageChops.difference(
                actual.crop((0, 0, 640, 332)), expected.crop((0, 0, 640, 332))
            )
            assert max(high for _, high in difference.getextrema()) <= 3, frame
            base = reference_motion(assets, snapshot, frame)
            # Opaque face/table stays in front of glass effects and outside the lighting mask.
            for position in [(380, 245), (350, 290)]:
                assert (
                    max(
                        abs(a - b)
                        for a, b in zip(
                            actual.getpixel(position), base.getpixel(position), strict=True
                        )
                    )
                    <= 2
                )


def test_nonzero_range_and_split_do_not_restart_rain_or_light(tmp_path):
    assets, snapshot, settings = effect_fixture(tmp_path / "split effects")
    renderer = FFmpegRenderer(assets, settings)
    profile = OutputProfile(
        id="effects",
        canvas=Canvas(width=640, height=360),
        fps=snapshot.episode.fps,
        container="mp4",
        video_codec="libx264",
        pixel_format="yuv420p",
        color_space="bt709",
    )
    decoded = []
    for start, end in [(137, 161), (137, 150), (150, 161)]:
        path = tmp_path / f"{start}-{end}.mp4"
        renderer.clip(snapshot, start, end, path, profile)
        raw = run_tool(
            [
                settings.ffmpeg,
                "-v",
                "error",
                "-nostdin",
                "-i",
                str(path),
                "-f",
                "rawvideo",
                "-pix_fmt",
                "rgb24",
                "-",
            ],
            max_bytes=(end - start) * 640 * 360 * 3,
        )
        pixels = (
            np.frombuffer(raw, dtype=np.uint8).reshape(end - start, 360, 640, 3).astype(np.int16)
        )
        decoded.append(pixels)
        for frame in [start, end - 1]:
            # The independently composed RGB reference must pass through the same documented
            # 4:2:0 color interchange before comparing codec pixels at saturated one-pixel edges.
            reference_path = tmp_path / f"reference-{start}-{frame}.png"
            reference_motion(assets, snapshot, frame, effects=True).save(reference_path)
            reference_raw = run_tool(
                [
                    settings.ffmpeg,
                    "-v",
                    "error",
                    "-nostdin",
                    "-i",
                    str(reference_path),
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
            reference = (
                np.frombuffer(reference_raw, dtype=np.uint8).reshape(360, 640, 3).astype(np.int16)
            )
            assert np.quantile(np.abs(pixels[frame - start, :332] - reference[:332]), 0.999) <= 15
    # Different GOP placement changes lossy pixels slightly; global effect phase stays fixed.
    split = np.concatenate(decoded[1:])
    assert np.quantile(np.abs(decoded[0] - split), 0.999) <= 10
