import json
from pathlib import Path

import pytest

from tabi.core.documents import parse_document
from tabi.core.models.base import content_hash

REPOSITORY = Path(__file__).resolve().parents[1]


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
