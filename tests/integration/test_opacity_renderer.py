import os
from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from PIL import Image

from tabi.core.assets import AssetService
from tabi.core.config import load_settings
from tabi.core.fixtures import generate_fixtures
from tabi.core.models import Episode
from tabi.core.models.base import FrameRate
from tabi.core.persistence import ProjectStore
from tabi.core.process import run_tool
from tabi.core.render.ffmpeg import GraphBuilder
from tabi.core.render.motion import value_expression
from tabi.core.timeline import Timeline

pytestmark = pytest.mark.media


@pytest.mark.parametrize("rate", [FrameRate(num=30, den=1), FrameRate(num=30000, den=1001)])
def test_frame_lookup_opacity_matches_legacy_pixels_through_fractional_timestamps(tmp_path, rate):
    root = tmp_path / "Opacity 東京"
    generate_fixtures(root, profile="effects")
    assets = AssetService(ProjectStore(root))
    settings = load_settings(None, env=os.environ, cwd=Path.cwd(), home=Path.home())
    episode = assets.store.read("episodes/episode.synthetic.json")
    ramp = np.arange(256, dtype=np.uint8).reshape(8, 32)
    source = tmp_path / "alpha ramp.png"
    Image.fromarray(ramp).save(source)
    spec = SimpleNamespace(strength_target="rain_amount", default_strength=0)
    for interpolation in ("linear", "constant"):
        data = episode.model_dump()
        next(c for c in data["curves"] if c["target"] == "rain_amount")["interpolation"] = (
            interpolation
        )
        timeline = Timeline(Episode.model_validate(data))
        builder = SimpleNamespace(rate=rate, timeline=timeline)
        for first, end in ((59, 123), (207, 213), (297, 300)):
            expression = value_expression(timeline, "train", "rain_amount", f"(N+{first})")
            filters = (
                GraphBuilder.effect_opacity(builder, episode.scenes[0], spec, first, end, "test"),
                f"geq=lum='lum(X,Y)*({expression})'",
            )
            arrays = []
            for filter_text in filters:
                raw = run_tool(
                    [
                        settings.ffmpeg,
                        "-v",
                        "error",
                        "-nostdin",
                        "-loop",
                        "1",
                        "-framerate",
                        f"{rate.num}/{rate.den}",
                        "-i",
                        str(source),
                        "-filter_threads",
                        "1",
                        "-vf",
                        f"format=gray,{filter_text}",
                        "-frames:v",
                        str(end - first),
                        "-pix_fmt",
                        "gray",
                        "-f",
                        "rawvideo",
                        "-",
                    ],
                    timeout=30,
                )
                arrays.append(
                    np.frombuffer(raw, dtype=np.uint8).reshape(end - first, 256).astype(np.int16)
                )
            assert int(np.max(np.abs(arrays[0] - arrays[1]))) <= 1
            if interpolation == "constant" and first == 59:
                assert arrays[0][120 - first, 255] == 63 and arrays[0][119 - first, 255] == 0
    # Extreme custom rates retain the earlier frame-expression path rather than
    # relying on sendcmd timestamps finer than its microsecond representation.
    builder.rate = FrameRate(num=1001, den=1)
    assert Fraction(builder.rate.num, builder.rate.den) > 1000
    assert GraphBuilder.effect_opacity(builder, episode.scenes[0], spec, 0, 2, "test").startswith(
        "geq="
    )
