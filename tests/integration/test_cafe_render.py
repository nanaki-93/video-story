import os
from pathlib import Path

import pytest
from PIL import Image, ImageChops

from tabi.core.assets import AssetService
from tabi.core.config import load_settings
from tabi.core.editor import EditorService, EditRequest
from tabi.core.fixtures import generate_fixtures
from tabi.core.jobs import JobService
from tabi.core.persistence import ProjectStore
from tabi.core.render.ffmpeg import FFmpegRenderer
from tabi.core.render.profiles import preset_profile
from tabi.core.timeline.compiler import ActionCompiler


@pytest.mark.media
def test_cafe_static_architecture_mask_anchor_and_real_export(tmp_path):
    root = tmp_path / "Café 東京"
    generate_fixtures(root, profile="cafe")
    service = AssetService(ProjectStore(root))
    editor = EditorService(service)
    original = editor.episode("episode.synthetic")
    # Same semantic editor used by the web API, with no scene-name switch.
    curve = original.curves[0].model_dump(mode="json")
    curve["keys"][0]["value"] = 18
    episode = editor.edit(
        original.id,
        EditRequest(expected_revision=0, command={"kind": "put_curve", "curve": curve}),
    )
    snapshot = ActionCompiler(service, purpose="synthetic_test").compile(episode)
    config = load_settings(None, env=os.environ, cwd=Path.cwd(), home=Path.home())
    renderer = FFmpegRenderer(service, config)
    images = []
    for frame in (0, 150, 240):
        path = root / f"cafe-{frame}.png"
        renderer.frame(snapshot, frame, path)
        with Image.open(path) as image:
            images.append(image.convert("RGB"))
    first, middle, last = images
    for other in (middle, last):
        # Room and building facades stay fixed; a train-like scrolling backdrop would fail.
        for region in ((0, 48, 90, 190), (245, 125, 580, 170), (236, 46, 244, 250)):
            assert ImageChops.difference(first.crop(region), other.crop(region)).getbbox() is None
    assert ImageChops.difference(
        first.crop((245, 65, 589, 105)), last.crop((245, 65, 589, 105))
    ).getbbox()
    # Different anchor: character is left of the window and the tabletop occludes its feet.
    assert (
        max(abs(a - b) for a, b in zip(first.getpixel((144, 240)), (244, 184, 120), strict=True))
        <= 2
    )
    assert first.getpixel((145, 287)) == (176, 120, 76)
    # The single pedestrian moves left; its figure cannot appear outside the white mask.
    assert middle.getpixel((502, 195)) != first.getpixel((502, 195))
    digest = service.store.save_snapshot(snapshot)
    jobs = JobService(service, config)
    job = jobs.submit(
        digest,
        preset_profile("proxy", fps=episode.fps),
        "exports/cafe.mp4",
        max_chunk_frames=150,
    )
    result = jobs.work(once=True)[0]
    assert result.id == job.id and result.state == "verified", result.error
    verified = jobs.verify_export(job.id)
    assert verified.video.frame_count == 300 and verified.audio.decoded_samples == 480000
    assert all(c.state == "verified" for c in result.chunks)
