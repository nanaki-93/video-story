import os
from pathlib import Path

import pytest
from PIL import Image

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
def test_real_activity_transitions_and_outfit_render(tmp_path):
    root = tmp_path / "Activity café 東京"
    generate_fixtures(root, profile="activities")
    assets = AssetService(ProjectStore(root))
    editor = EditorService(assets)
    episode = editor.episode("episode.synthetic")
    snapshot = ActionCompiler(assets, purpose="synthetic_test").compile(episode)
    config = load_settings(None, env=os.environ, cwd=Path.cwd(), home=Path.home())
    renderer = FFmpegRenderer(assets, config)
    for frame in (0, 53, 90, 131, 137, 180, 215, 221, 270, 299):
        renderer.frame(snapshot, frame, root / f"activity-{frame}.png")
    jobs = JobService(assets, config)
    digest = assets.store.save_snapshot(snapshot)
    job = jobs.submit(
        digest,
        preset_profile("proxy", fps=episode.fps),
        "exports/activities.mp4",
        max_chunk_frames=90,
    )
    completed = jobs.work(once=True)[0]
    assert completed.state == "verified", completed.error
    assert jobs.verify_export(job.id).audio.decoded_samples == 480000
    changed = editor.edit(
        episode.id,
        EditRequest(
            expected_revision=0,
            command={
                "kind": "change_pack",
                "scene_id": "cafe",
                "pack": {"id": "pack.synthetic.activities.amber", "version": "1.0"},
            },
        ),
    )
    amber = ActionCompiler(assets, purpose="synthetic_test").compile(changed)
    renderer.frame(amber, 90, root / "activity-amber-90.png")
    with (
        Image.open(root / "activity-90.png") as first,
        Image.open(root / "activity-amber-90.png") as second,
    ):
        # Only the deliberately authored geometric outfit changes; the face stays identical.
        assert (
            first.crop((125, 222, 160, 238)).tobytes()
            == second.crop((125, 222, 160, 238)).tobytes()
        )
        assert first.getpixel((141, 267)) != second.getpixel((141, 267))
