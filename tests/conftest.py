import json
from pathlib import Path

import pytest

from tabi.core.documents import parse_document
from tabi.core.models.base import content_hash

REPOSITORY = Path(__file__).resolve().parents[1]


def pytest_addoption(parser):
    parser.addoption("--run-media", action="store_true", help="Run actual FFmpeg render checks")


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--run-media"):
        for item in items:
            if "media" in item.keywords:
                item.add_marker(
                    pytest.mark.skip(reason="Run make test-media for actual FFmpeg checks")
                )


@pytest.fixture
def episode_data():
    return json.loads((REPOSITORY / "examples/episode.pilot.json").read_text())


@pytest.fixture
def project_data():
    return {
        "schema_version": "1.0",
        "document_type": "project",
        "id": "test-project",
        "title": "Synthetic project / 東京",
        "revision": 0,
        "created_at": "2026-10-03T00:00:00Z",
        "updated_at": "2026-10-03T00:00:00Z",
    }


@pytest.fixture
def asset_data():
    return json.loads((REPOSITORY / "examples/asset.synthetic.json").read_text())


@pytest.fixture
def snapshot_data(episode_data):
    # A schema fixture, not compiler output. Hash the actual template document.
    episode_data.update(actions=[], tracks=[], events=[], asset_locks=[])
    template = parse_document((REPOSITORY / "examples/scene.train.json").read_bytes())
    fixture_hash = content_hash({"name": "synthetic schema test", "version": "1"})
    return {
        "schema_version": "1.0",
        "document_type": "compiled_snapshot",
        "id": "test-snapshot",
        "purpose": "synthetic_test",
        "episode": episode_data,
        "locked_assets": [
            {"id": template.id, "version": template.version, "sha256": content_hash(template)}
        ],
        "schedule": [],
        "audio_placements": [],
        "compiler": {"name": "synthetic-test-fixture", "version": "1", "sha256": fixture_hash},
        "prng": {"name": "synthetic-test-fixture", "version": "1", "sha256": fixture_hash},
    }


@pytest.fixture
def review_project(tmp_path):
    """Temporary test-only supplied records exercise approval; no actual artwork is approved."""
    from PIL import Image, ImageCms

    from tabi.core.assets import AssetService
    from tabi.core.authoring import AuthoringService
    from tabi.core.models import Episode, ImportRequest
    from tabi.core.models.base import AssetRef
    from tabi.core.persistence import ProjectStore

    sources = tmp_path / "Test originals 東京"
    sources.mkdir()
    profile = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
    Image.new("RGB", (64, 36), (30, 50, 80)).save(sources / "background.png", icc_profile=profile)
    for index, color in enumerate([(230, 80, 50, 255), (220, 90, 40, 255)]):
        Image.new("RGBA", (16, 16), color).save(sources / f"pose-{index}.png", icc_profile=profile)
    store = ProjectStore.initialize(tmp_path / "Review flow 東京", "Temporary review guard test")
    author = AuthoringService(AssetService(store, roots={"originals": sources}))
    provenance = {
        "origin": "user_supplied",
        "creator": "Temporary automated test",
        "commercial_use": "confirmed",
        "notes": "Test-only policy records for owned geometry; no real art or rights approval.",
    }
    for identity, kind, names in [
        ("test-background", "still", ["background.png"]),
        ("test-body", "sequence", ["pose-0.png", "pose-1.png"]),
    ]:
        author.assets.import_asset(
            ImportRequest.model_validate(
                {
                    "id": identity,
                    "version": "1.0",
                    "kind": kind,
                    "paths": [{"root_id": "originals", "path": name} for name in names],
                    "fps": {"num": 30, "den": 1} if kind == "sequence" else None,
                    "provenance": provenance,
                    "compatibility": {"cameras": ["test-camera"], "channels": ["body"]},
                }
            )
        )
    template = author.install(
        {
            "schema_version": "1.0",
            "document_type": "scene_template",
            "id": "test-template",
            "version": "1.0",
            "camera_id": "test-camera",
            "design_canvas": {"width": 64, "height": 36},
            "capabilities": [],
            "channels": ["body"],
            "anchors": {"seat": {"x": 32, "y": 30}},
            "slots": [
                {
                    "id": "background",
                    "kind": "still",
                    "z": 0,
                    "asset": {"id": "test-background", "version": "1.0"},
                },
                {"id": "body", "kind": "character", "z": 1, "anchor": "seat"},
            ],
            "mask_semantics": "white_visible_black_hidden",
        }
    )
    pack = author.install(
        {
            "schema_version": "1.0",
            "document_type": "action_pack",
            "id": "test-pack",
            "version": "1.0",
            "template": {"id": template.id, "version": template.version},
            "camera_id": "test-camera",
            "canvas": {"width": 16, "height": 16},
            "anchor": {"x": 8, "y": 16},
            "fps": {"num": 30, "den": 1},
            "alpha_mode": "straight",
            "actions": [
                {
                    "id": "idle",
                    "version": "1.0",
                    "channel": "body",
                    "start_pose": "idle",
                    "end_pose": "idle",
                    "kind": "loop",
                    "frame_count": 2,
                    "clip": {"id": "test-body", "version": "1.0"},
                    "loop": {"start_frame": 0, "end_frame": 2},
                }
            ],
        }
    )
    episode = author.install(
        Episode(
            schema_version="1.0",
            document_type="episode",
            id="review-episode",
            title="Temporary approval flow",
            format="story",
            fps={"num": 30, "den": 1},
            canvas={"width": 64, "height": 36},
            duration_frames=30,
            seed=0,
            scenes=[
                {
                    "id": "scene",
                    "template": AssetRef(id=template.id, version=template.version),
                    "start_frame": 0,
                    "end_frame": 30,
                    "initial_state": {"body_pose": "idle"},
                }
            ],
            actions=[
                {
                    "id": "idle",
                    "scene_id": "scene",
                    "pack": AssetRef(id=pack.id, version=pack.version),
                    "action_id": "idle",
                    "version": "1.0",
                    "channel": "body",
                    "start_frame": 0,
                    "end_frame": 30,
                    "repeat": "loop_to_fill",
                }
            ],
        ).model_dump(mode="json")
    )
    return author, template, pack, episode
