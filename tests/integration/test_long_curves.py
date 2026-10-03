import os
from pathlib import Path

import pytest

from tabi.core.assets import AssetService
from tabi.core.config import load_settings
from tabi.core.fixtures import generate_fixtures
from tabi.core.models import Episode
from tabi.core.persistence import ProjectStore
from tabi.core.process import run_tool
from tabi.core.render.motion import distance_expression, value_expression
from tabi.core.timeline import Timeline


@pytest.mark.media
@pytest.mark.parametrize("interpolation,outside", [("linear", "clamp"), ("constant", "zero")])
def test_dense_long_curves_preserve_global_integrals_and_values(tmp_path, interpolation, outside):
    root = tmp_path / "Dense curves"
    generate_fixtures(root)
    assets = AssetService(ProjectStore(root))
    data = assets.store.read("episodes/episode.synthetic.json").model_dump()
    data["duration_frames"] = 8100
    data["scenes"][0].update(end_frame=8100, final_state=None)
    curve = data["curves"][0]
    curve.update(
        interpolation=interpolation,
        outside=outside,
        keys=[{"frame": n * 3 + 3, "value": (n % 11) * 10} for n in range(2400)],
    )
    timeline = Timeline(Episode.model_validate(data))
    settings = load_settings(None, env=os.environ, cwd=Path.cwd(), home=Path.home())
    for first, end in [(0, 8), (7194, 7205)]:
        for kind in ("distance", "value"):
            fn = distance_expression if kind == "distance" else value_expression
            args = (timeline, "train") + (() if kind == "distance" else ("travel_speed",))
            expression = fn(*args, f"(N+{first})", first_frame=first, end_frame=end)
            assert len(expression) < 2500  # Unrelated 2390+ keys do not enter this graph.
            raw = run_tool(
                [
                    settings.ffmpeg,
                    "-v",
                    "error",
                    "-nostdin",
                    "-f",
                    "lavfi",
                    "-i",
                    "color=s=16x16:r=30",
                    "-vf",
                    f"format=gray,geq=lum='mod(floor(({expression})+0.000001),251)'",
                    "-frames:v",
                    str(end - first),
                    "-pix_fmt",
                    "gray",
                    "-f",
                    "rawvideo",
                    "-",
                ]
            )
            assert len(raw) == 256 * (end - first)
            for offset, frame in enumerate(range(first, end)):
                value = (
                    timeline.travel_at("train", frame)
                    if kind == "distance"
                    else timeline.value_at("train", "travel_speed", frame)
                )
                expected = (value.numerator // value.denominator) % 251
                assert set(raw[offset * 256 : (offset + 1) * 256]) == {expected}
