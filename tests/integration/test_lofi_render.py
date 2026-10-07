"""Actual frame/pixel and nonzero-range tests for independent prepared overlay loops."""

import os
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from tabi.core.config import load_settings
from tabi.core.fixture_lofi import generate_lofi_fixtures
from tabi.core.lofi import LofiService
from tabi.core.models.base import AssetRef
from tabi.core.models.lofi import CreateLofiVideo
from tabi.core.models.production import OutputProfile
from tabi.core.process import run_tool
from tabi.core.render.ffmpeg import FFmpegRenderer
from tabi.core.timeline.compiler import ActionCompiler

pytestmark = pytest.mark.media


def prepared(tmp_path):
    assets, scene = generate_lofi_fixtures(tmp_path / "Asset video 東京")
    service = LofiService(assets)
    scene = service.save(scene, expected_revision=None)
    episode = service.create_video(
        CreateLofiVideo(
            id="loop.video",
            title="SYNTHETIC loop verification",
            scene=AssetRef(id=scene.id, version=scene.version),
            expected_scene_revision=0,
            duration_seconds=3,
        )
    )
    snapshot = ActionCompiler(assets, purpose="synthetic_test").compile(episode)
    settings = load_settings(None, env=os.environ, cwd=Path.cwd(), home=Path.home())
    return assets, scene, snapshot, settings


def test_master_and_scenery_remain_independent_of_blink_and_loop_gap(tmp_path):
    assets, scene, snapshot, settings = prepared(tmp_path)
    renderer = FFmpegRenderer(assets, settings)
    # Independently stated expected overlay values at the start, active frames, gap and repeat.
    eye_colors = {
        0: (220, 210, 190),
        2: (220, 210, 190),
        3: (220, 80, 70),
        4: (50, 30, 40),
        5: (220, 210, 190),
        14: (220, 210, 190),
        16: (220, 80, 70),
        17: (50, 30, 40),
        30: (50, 30, 40),
    }
    for frame, eyes in eye_colors.items():
        path = tmp_path / f"frame-{frame}.png"
        renderer.frame(snapshot, frame, path)
        with Image.open(path) as image:
            for point, expected in [
                ((70, 70), eyes),
                ((50, 100), (120, 174, 155)),
                ((200, 70), (50 + ((200 + frame) % 128), 110, 165)),
            ]:
                assert (
                    max(abs(a - b) for a, b in zip(image.getpixel(point), expected, strict=True))
                    <= 2
                ), (frame, point)
    assert assets.require_valid(scene.master).provenance.origin == "synthetic"


def test_nonzero_ranges_and_chunk_boundaries_preserve_every_overlay_and_scenery_frame(tmp_path):
    _, _, snapshot, settings = data = prepared(tmp_path)
    renderer = FFmpegRenderer(data[0], settings)
    profile = OutputProfile(
        id="lofi.test",
        canvas=snapshot.episode.canvas,
        fps=snapshot.episode.fps,
        container="mp4",
        video_codec="libx264",
        pixel_format="yuv420p",
        color_space="bt709",
    )
    frames = []
    for start, end in [(11, 35), (11, 19), (19, 35)]:
        path = tmp_path / f"loop-{start}-{end}.mp4"
        renderer.clip(snapshot, start, end, path, profile)
        raw = run_tool(
            [
                settings.ffmpeg,
                "-v",
                "error",
                "-i",
                str(path),
                "-f",
                "rawvideo",
                "-pix_fmt",
                "rgb24",
                "-",
            ],
            max_bytes=(end - start) * 320 * 180 * 3,
        )
        frames.append(
            np.frombuffer(raw, dtype=np.uint8).reshape(end - start, 180, 320, 3).astype(np.int16)
        )
    assert np.quantile(np.abs(frames[0] - np.concatenate(frames[1:])), 0.999) <= 10
    # No phase restart at the second chunk: global frame 19 is in a transparent blink gap.
    assert np.max(np.abs(frames[2][0, 70, 70] - np.array([220, 210, 190]))) <= 6
