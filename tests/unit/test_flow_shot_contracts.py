from copy import deepcopy

import pytest
from pydantic import ValidationError
from test_flow_contracts import episode_data

from tabi.core.models.base import content_hash
from tabi.core.models.flow import FlowEpisode, FlowRecipe, FlowReference


def shot_episode_data():
    data = episode_data()
    data["recipe"] = {
        "target_frames": 384,
        "shots": [
            {
                "id": identity,
                "title": identity,
                "reference_key": key,
                "framing": key,
                "duration_frames": 192,
                "beats": [{"id": identity, "kind": "rest", "target_frame": 0}],
            }
            for identity, key in [("breathe", "wide"), ("watch", "close")]
        ],
    }
    data["references"] = [
        {
            "title": key,
            "key": key,
            "media": deepcopy(data["candidates"][0]["media"]),
            "starting_state": {"pose": "watching"},
            "review_note": "Synthetic contract fixture; no publication approval.",
            "synthetic": True,
        }
        for key in ("wide", "close")
    ]
    data["attempts"][0].update(shot_id="breathe", mode="shot_start", template_version="2")
    second_attempt = deepcopy(data["attempts"][0])
    second_attempt.update(id="second", shot_id="watch", parent_id="clip1", parent_sha256="c" * 64)
    data["attempts"].append(second_attempt)
    second = deepcopy(data["candidates"][0])
    second.update(
        id="clip2",
        attempt_id="second",
        parent_id="clip1",
        parent_sha256="c" * 64,
        reviewed_sha256="d" * 64,
    )
    second["media"]["sha256"] = "d" * 64
    data["candidates"].append(second)
    data["accepted_ids"].append("clip2")
    return data


def test_clean_shots_keep_editorial_lineage_without_extending_old_pixels():
    episode = FlowEpisode.model_validate(shot_episode_data())
    assert episode.accepted_frames == 384
    assert episode.attempts[1].mode == "shot_start"
    assert episode.attempts[1].parent_id == "clip1"
    assert FlowEpisode.model_validate_json(episode.model_dump_json()) == episode


@pytest.mark.parametrize(
    "fault", ["duration", "order", "duplicate", "fractional", "cross_extend", "overrun", "ref"]
)
def test_invalid_shot_schedules_and_cross_camera_generation_fail(fault):
    data = shot_episode_data()
    if fault == "duration":
        data["recipe"]["target_frames"] = 385
    elif fault == "order":
        data["recipe"]["shots"].reverse()
    elif fault == "duplicate":
        data["recipe"]["shots"][1]["id"] = "breathe"
    elif fault == "fractional":
        data["recipe"]["shots"][0]["duration_frames"] = 192.0
    elif fault == "cross_extend":
        data["attempts"][1]["mode"] = "extend"
    elif fault == "overrun":
        data["candidates"][0]["frame_count"] = 193
        data["candidates"][0]["trim"]["end_frame"] = 193
    else:
        data["references"].pop()
    with pytest.raises(ValidationError):
        FlowEpisode.model_validate(data)


def test_keyed_starting_frames_require_visual_facts_and_cannot_duplicate():
    data = shot_episode_data()
    del data["references"][0]["starting_state"]
    with pytest.raises(ValidationError, match="reviewed visible"):
        FlowEpisode.model_validate(data)
    data = shot_episode_data()
    data["references"].append(data["references"][0])
    with pytest.raises(ValidationError, match="duplicate reference"):
        FlowEpisode.model_validate(data)


def test_legacy_hashes_and_optional_reference_serialization_are_unchanged():
    episode = FlowEpisode.model_validate(episode_data())
    assert content_hash(episode.recipe) == (
        "ba508841a75ad02fb43892f1f020ba8cbccae3b88436da2cb06ce38e82b608b2"
    )
    assert content_hash(episode.attempts[0]) == (
        "180138694ccf892e231d01c6ff0761357097f355284f7b44ef6ced0e1504d01e"
    )
    raw = {
        "title": "Old reference",
        "media": episode.candidates[0].media.model_dump(mode="json"),
        "rights": "pending",
        "synthetic": False,
    }
    assert FlowReference.model_validate(raw).model_dump(mode="json") == raw
    assert "shots" not in episode.recipe.model_dump()
    assert "estimated_start_credit" not in episode.limits.model_dump()


def test_shot_exterior_is_optional_strict_and_does_not_change_old_recipe_hashes():
    data = shot_episode_data()
    legacy = FlowRecipe.model_validate(data["recipe"])
    assert all("exterior" not in shot for shot in legacy.model_dump()["shots"])
    explicit_none = deepcopy(data["recipe"])
    for shot in explicit_none["shots"]:
        shot["exterior"] = None
    assert content_hash(FlowRecipe.model_validate(explicit_none)) == content_hash(legacy)
    scenic = deepcopy(data["recipe"])
    scenic["shots"][0]["exterior"] = "Sumida River, reflections and a distant skyline."
    assert content_hash(FlowRecipe.model_validate(scenic)) != content_hash(legacy)
    scenic["shots"][0]["exterior"] = ""
    with pytest.raises(ValidationError):
        FlowRecipe.model_validate(scenic)
    scenic["shots"][0]["exterior"] = 123
    with pytest.raises(ValidationError):
        FlowRecipe.model_validate(scenic)


def test_different_window_views_cannot_share_one_starting_image_key():
    data = shot_episode_data()["recipe"]
    data["shots"][1]["reference_key"] = data["shots"][0]["reference_key"]
    data["shots"][0]["exterior"] = "River and bridge."
    data["shots"][1]["exterior"] = "Shopping street."
    with pytest.raises(ValidationError, match="distinct starting references"):
        FlowRecipe.model_validate(data)
    data["shots"][1]["exterior"] = "River and bridge."
    assert FlowRecipe.model_validate(data).shots[1].exterior == "River and bridge."


def test_distinct_reference_keys_cannot_disguise_one_reused_exterior_image():
    data = shot_episode_data()
    for shot, exterior in zip(
        data["recipe"]["shots"], ["River and bridge.", "Shopping street."], strict=True
    ):
        shot["exterior"] = exterior
    with pytest.raises(ValidationError, match="same image content"):
        FlowEpisode.model_validate(data)
    data["references"][1]["media"]["sha256"] = "e" * 64
    assert len(FlowEpisode.model_validate(data).references) == 2


def test_assigned_scenery_does_not_allow_a_district_change_inside_the_shot():
    data = shot_episode_data()["recipe"]
    data["shots"][0]["exterior"] = "River and bridge."
    data["shots"][0]["beats"].append(
        {"id": "district-change", "kind": "district", "target_frame": 96, "district": "Ginza"}
    )
    with pytest.raises(ValidationError, match="new camera cut"):
        FlowRecipe.model_validate(data)
