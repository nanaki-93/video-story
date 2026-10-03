import hashlib
import os
from pathlib import Path

import pytest
from PIL import Image, ImageChops

from tabi.core.assets import AssetService
from tabi.core.config import load_settings
from tabi.core.fixtures import generate_fixtures
from tabi.core.models import Asset, SceneTemplate
from tabi.core.models.base import AssetRef, Canvas
from tabi.core.models.production import OutputProfile
from tabi.core.persistence import ProjectStore
from tabi.core.process import run_tool
from tabi.core.render.backend import RenderError
from tabi.core.render.ffmpeg import FFmpegRenderer
from tabi.core.timeline.compiler import ActionCompiler

pytestmark = pytest.mark.media


def static_fixture(root):
    """T11 uses explicitly cropped stationary strips; motion is introduced in T12."""
    generate_fixtures(root)
    store = ProjectStore(root)
    template = store.read("registry/templates/scene.synthetic.train/1.0.json")
    data = template.model_dump(mode="json")
    data["slots"] = [slot for slot in data["slots"] if slot["kind"] != "scheduled_sprite"]
    for slot in data["slots"]:
        if slot["kind"] == "tile_strip":
            slot.update(kind="still", tile_period=None)
            asset = store.read(f"registry/assets/{slot['asset']['id']}/1.0.json")
            raw = asset.model_dump(mode="json")
            raw["compatibility"]["crop"] = {"x": 0, "y": 0, "width": 640, "height": 360}
            store.save_draft(Asset.model_validate(raw), expected_revision=asset.revision)
    store.save_draft(SceneTemplate.model_validate(data), expected_revision=template.revision)
    episode = store.read("episodes/episode.synthetic.json")
    episode = episode.model_copy(update={"events": []})
    service = AssetService(store)
    snapshot = ActionCompiler(service, purpose="synthetic_test").compile(episode)
    return service, snapshot


def settings():
    return load_settings(None, env=os.environ, cwd=Path.cwd(), home=Path.home())


def reference_frame(service, frame):
    """Independent RGBA composition in Pillow, outside the FFmpeg graph builder."""

    def image(name, index=None):
        asset = service.load(AssetRef(id=f"fixture.{name}", version="1.0"))
        with Image.open(service.resolve(asset.files[index or 0].location)) as source:
            return source.convert("RGBA")

    result = image("cabin")
    mask = image("window").convert("L")
    for name in ["far", "mid", "near"]:
        exterior = image(name).crop((0, 0, 640, 360))
        exterior.putalpha(ImageChops.multiply(exterior.getchannel("A"), mask))
        result = Image.alpha_composite(result, exterior)
    if frame < 84:
        action, source_frame = "idle", frame % 12
    elif frame < 90:
        action, source_frame = "entry", frame - 84
    elif frame < 210:
        action, source_frame = "observe", (frame - 90) % 12
    elif frame < 216:
        action, source_frame = "exit", frame - 210
    else:
        action, source_frame = "idle", (frame - 216) % 12
    result.alpha_composite(image(action, source_frame), (322, 202))
    for start in [36, 270]:
        if start <= frame < start + 6:
            result.alpha_composite(image("blink", frame - start), (322, 202))
    return Image.alpha_composite(result, image("foreground")).convert("RGB")


@pytest.mark.parametrize("partial", [False, True])
def test_actual_still_pixels_match_independent_mask_alpha_and_occlusion(tmp_path, partial):
    service, snapshot = static_fixture(tmp_path / "Marco's 東京 stills")
    if partial:
        for name in ("window", "near"):
            record = service.load(AssetRef(id=f"fixture.{name}", version="1.0"))
            path = service.resolve(record.files[0].location)
            with Image.open(path) as original:
                original.load()
                image = original.copy()
            if name == "window":
                image = image.point(lambda value: value // 2)
            else:
                image.putalpha(image.getchannel("A").point(lambda value: value // 2))
            image.save(path)
            data = record.model_dump(mode="json")
            data["files"][0].update(
                sha256=hashlib.sha256(path.read_bytes()).hexdigest(), size_bytes=path.stat().st_size
            )
            service.store.save_draft(Asset.model_validate(data), expected_revision=record.revision)
        snapshot = ActionCompiler(service, purpose="synthetic_test").compile(snapshot.episode)
    renderer = FFmpegRenderer(service, settings())
    for frame in [37, 84, 89, 90, 215, 216]:
        output = tmp_path / f"frame-{frame}.png"
        report = renderer.frame(snapshot, frame, output)
        assert report.full_decode_passed and not report.timestamps_verified
        with Image.open(output) as rendered:
            expected = reference_frame(service, frame)
            # The bottom 28 rows contain the required draft label.
            difference = ImageChops.difference(
                rendered.crop((0, 0, 640, 332)), expected.crop((0, 0, 640, 332))
            )
            assert max(high for low, high in difference.getextrema()) <= 2
    assert not list(tmp_path.glob(".tabi-render-*"))


def test_actual_range_video_matches_exact_frame_inspection(tmp_path):
    service, snapshot = static_fixture(tmp_path / "clip source")
    config = settings()
    renderer = FFmpegRenderer(service, config)
    profile = OutputProfile(
        id="test.proxy",
        canvas=Canvas(width=640, height=360),
        fps=snapshot.episode.fps,
        container="mp4",
        video_codec="libx264",
        pixel_format="yuv420p",
        color_space="bt709",
    )
    output = tmp_path / "Test's 東京 range.mp4"
    report = renderer.clip(snapshot, 80, 100, output, profile)
    assert report.frame_count == 20 and report.timestamps_verified
    raw = run_tool(
        [
            config.ffmpeg,
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
        max_bytes=640 * 360 * 3 * 20,
    )
    stride = 640 * 360 * 3
    for local in [0, 3, 4, 9, 10, 19]:
        decoded = Image.frombytes("RGB", (640, 360), raw[local * stride : (local + 1) * stride])
        reference = reference_frame(service, 80 + local)
        for x, y in [(12, 100), (80, 80), (200, 180), (370, 222), (370, 260), (370, 300)]:
            assert (
                max(
                    abs(a - b)
                    for a, b in zip(
                        decoded.getpixel((x, y)), reference.getpixel((x, y)), strict=True
                    )
                )
                <= 15
            )
    before = output.read_bytes()
    with pytest.raises(RenderError, match="exists"):
        renderer.clip(snapshot, 80, 100, output, profile)
    assert output.read_bytes() == before


def test_missing_lock_never_publishes(tmp_path):
    service, snapshot = static_fixture(tmp_path / "invalid")
    renderer = FFmpegRenderer(service, settings())
    record = service.load(AssetRef(id="fixture.cabin", version="1.0"))
    data = record.model_dump(mode="json")
    data["provenance"]["notes"] = "Changed after freeze"
    service.store.save_draft(Asset.model_validate(data), expected_revision=record.revision)
    output = tmp_path / "must-not-exist.png"
    with pytest.raises(RenderError, match="lock changed"):
        renderer.frame(snapshot, 37, output)
    assert not output.exists()


def test_invalid_mask_canvas_never_publishes(tmp_path):
    service, snapshot = static_fixture(tmp_path / "invalid mask")
    record = service.load(AssetRef(id="fixture.window", version="1.0"))
    data = record.model_dump(mode="json")
    data["compatibility"]["crop"] = {"x": 0, "y": 0, "width": 320, "height": 180}
    service.store.save_draft(Asset.model_validate(data), expected_revision=record.revision)
    snapshot = ActionCompiler(service, purpose="synthetic_test").compile(snapshot.episode)
    output = tmp_path / "invalid-mask.png"
    with pytest.raises(RenderError, match="mask canvas"):
        FFmpegRenderer(service, settings()).frame(snapshot, 37, output)
    assert not output.exists()


def test_verification_failure_preserves_existing_source(tmp_path, monkeypatch):
    service, snapshot = static_fixture(tmp_path / "preservation")
    source = service.store.root / "assets/fixture.cabin/image.png"
    before = source.read_bytes()
    from tabi.core.render import ffmpeg

    def fail(*args):
        raise RenderError("synthetic verification rejection")

    monkeypatch.setattr(ffmpeg, "verify_video", fail)
    profile = OutputProfile(
        id="proxy",
        canvas=Canvas(width=640, height=360),
        fps=snapshot.episode.fps,
        container="mp4",
        video_codec="libx264",
        pixel_format="yuv420p",
        color_space="bt709",
    )
    output = tmp_path / "no-final.mp4"
    with pytest.raises(RenderError, match="verification rejection"):
        FFmpegRenderer(service, settings()).clip(snapshot, 0, 3, output, profile)
    assert not output.exists() and source.read_bytes() == before
    assert not list(tmp_path.glob(".tabi-render-*"))
