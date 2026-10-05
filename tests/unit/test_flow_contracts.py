import hashlib

import pytest
from pydantic import ValidationError

from tabi.core.documents import DocumentError, parse_document
from tabi.core.models.base import canonical_bytes
from tabi.core.models.flow import FlowEpisode, FlowRecipe, FlowState


def episode_data():
    prompt = "Continue quiet breathing."
    return {
        "schema_version": "1.0",
        "id": "train",
        "title": "Tokyo",
        "recipe": {},
        "limits": {
            "credit_ceiling": 70,
            "remaining_allowance": 100,
            "estimated_credit_per_attempt": 5,
            "allowance_checked_at": "2026-10-06",
        },
        "attempts": [
            {
                "schema_version": "1.0",
                "id": "opening",
                "episode_id": "train",
                "recipe_sha256": "a" * 64,
                "references_sha256": "b" * 64,
                "beat": {"id": "rest", "kind": "rest", "target_frame": 0},
                "mode": "image_motion",
                "prompt": prompt,
                "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                "state": "received",
                "reserved_credits": 5,
            }
        ],
        "candidates": [
            {
                "id": "clip1",
                "attempt_id": "opening",
                "parent_id": None,
                "parent_sha256": None,
                "media": {
                    "location": {"path": "sources/東京 clip.mp4"},
                    "sha256": "c" * 64,
                    "size_bytes": 123,
                },
                "fps": {"num": 24, "den": 1},
                "canvas": {"width": 1280, "height": 720},
                "frame_count": 192,
                "trim": {"start_frame": 0, "end_frame": 192},
                "technical_ok": True,
                "review": "accepted",
                "reviewed_sha256": "c" * 64,
                "review_note": "Watched with the original reference.",
                "observed_state": {"pose": "watching"},
                "safe_end_frame": 192,
            }
        ],
        "accepted_ids": ["clip1"],
    }


def test_native_frame_duration_and_portable_roundtrip():
    episode = FlowEpisode.model_validate(episode_data())
    assert episode.accepted_frames == 192
    assert parse_document(canonical_bytes(episode)) == episode


@pytest.mark.parametrize("fault", ["approval", "hash", "trim", "parent", "fps", "receipt"])
def test_stale_or_unverified_candidates_cannot_enter_active_branch(fault):
    data = episode_data()
    candidate = data["candidates"][0]
    if fault == "approval":
        candidate["technical_ok"] = False
    elif fault == "hash":
        candidate["reviewed_sha256"] = "d" * 64
    elif fault == "trim":
        candidate["trim"]["end_frame"] = 193
    elif fault == "parent":
        candidate.update(parent_id="missing", parent_sha256="a" * 64)
    elif fault == "fps":
        candidate["fps"]["num"] = 30
    else:
        data["attempts"][0]["state"] = "submitted"
    with pytest.raises(ValidationError):
        FlowEpisode.model_validate(data)


def test_parent_cycle_and_prompt_mutation_are_rejected():
    data = episode_data()
    data["attempts"][0].update(mode="extend", parent_id="clip1", parent_sha256="c" * 64)
    data["candidates"][0].update(parent_id="clip1", parent_sha256="c" * 64)
    with pytest.raises(ValidationError, match="cycle"):
        FlowEpisode.model_validate(data)
    data = episode_data()
    data["attempts"][0]["prompt"] = "A different request"
    with pytest.raises(ValidationError, match="prompt hash"):
        FlowEpisode.model_validate(data)


def test_unknown_fields_major_versions_and_noninteger_frames_fail():
    data = episode_data()
    data["recipe"]["target_frames"] = 2160.0
    with pytest.raises(ValidationError):
        FlowEpisode.model_validate(data)
    data = episode_data()
    data.update(document_type="flow_episode", schema_version="2.0")
    with pytest.raises(DocumentError):
        parse_document(canonical_bytes(data))
    with pytest.raises(ValidationError):
        FlowRecipe.model_validate({"seed": 123})


def test_requested_props_do_not_override_observed_inventory_or_hands():
    with pytest.raises(ValidationError):
        FlowState(cup_kind="takeaway", cup_position="held", hands="resting")
    state = FlowState(cup_kind="takeaway", cup_position="table", hands="resting")
    assert state.has_saucer is None
    with pytest.raises(ValidationError):
        FlowRecipe(project_url="https://example.com/private")
    data = episode_data()
    data["limits"]["credit_ceiling"] = 101
    with pytest.raises(ValidationError):
        FlowEpisode.model_validate(data)
