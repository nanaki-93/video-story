import copy
import json

import pytest

from tabi.cli.main import main
from tabi.core.assets import AssetService
from tabi.core.fixtures import generate_fixtures
from tabi.core.models import Episode, SceneTemplate
from tabi.core.models.base import canonical_bytes
from tabi.core.models.scenes import Transition
from tabi.core.persistence import ProjectStore
from tabi.core.story import inspect_story
from tabi.core.timeline.compiler import ActionCompiler, CompileError
from tabi.core.timeline.transitions import validate_transitions


@pytest.fixture
def story(tmp_path):
    generate_fixtures(tmp_path / "Story 東京", profile="story")
    store = ProjectStore(tmp_path / "Story 東京")
    compiler = ActionCompiler(AssetService(store), purpose="synthetic_test")
    return store, compiler, store.read("episodes/episode.synthetic.json")


def test_story_links_state_at_overlap_start_and_keeps_auditable_intent(story, capsys):
    store, compiler, episode = story
    snapshot = compiler.compile(episode)
    assert snapshot.episode.scenes[0].final_state.travel_distance_px == 300
    assert snapshot.episode.scenes[1].initial_state.travel_distance_px == 180
    assert snapshot.episode.scenes[1].final_state.travel_distance_px == 780
    assert snapshot.episode.scenes[1].final_state.props == {"table": "seat"}
    report = inspect_story(snapshot)
    assert report.issues == []
    assert [boundary.sample for boundary in report.music_boundaries] == [0, 480000]
    assert all(boundary.purposes for boundary in report.music_boundaries)
    digest = store.save_snapshot(snapshot)
    assert main(["story", "inspect", digest, "--project", str(store.root)]) == 0
    assert json.loads(capsys.readouterr().out)["snapshot_sha256"] == digest
    wrong = episode.model_dump(mode="json")
    wrong["scenes"][1]["initial_state"]["travel_distance_px"] = 300
    with pytest.raises(CompileError, match="at entry"):
        compiler.compile(Episode.model_validate(wrong))


@pytest.mark.parametrize("defect", ["phase", "geometry", "face", "props", "clip"])
def test_matched_transition_rejects_character_divergence(story, defect):
    store, compiler, episode = story
    data = episode.model_dump(mode="json")
    if defect == "phase":
        snapshot = compiler.compile(episode)
        # Select by channel/scene, not schedule position, since events are interleaved.
        changed = [
            event.model_copy(update={"phase_origin_frame": 143})
            if getattr(event, "channel", None) == "body" and event.scene_id == "city"
            else event
            for event in snapshot.schedule
        ]
        with pytest.raises(ValueError, match="source frames and phase"):
            validate_transitions(snapshot.episode, changed, compiler.resolve)
        return
    if defect == "geometry":
        original = store.read("registry/templates/scene.synthetic.train/1.0.json")
        template = original.model_dump(mode="json")
        template["anchors"]["other"] = {"x": 380, "y": 294}
        store.save_draft(SceneTemplate.model_validate(template), expected_revision=0)
        data["scenes"][1]["anchor"] = "other"
    elif defect == "face":
        data["actions"][-1].update(start_frame=156, end_frame=162)
    elif defect == "props":
        data["events"].append(
            {
                "type": "prop",
                "id": "table-moves",
                "scene_id": "city",
                "frame": 160,
                "object_id": "table",
                "location": "away",
            }
        )
    else:
        for transition in [data["scenes"][0]["transition_out"], data["scenes"][1]["transition_in"]]:
            transition["match_action"]["id"] = "fixture.observe"
    with pytest.raises(ValueError, match="placement/camera|divergent|declared prepared clip"):
        compiler.compile(Episode.model_validate(data))


def test_single_visible_is_limited_to_one_character_scene(story):
    store, compiler, episode = story
    data = episode.model_dump(mode="json")
    for transition in [data["scenes"][0]["transition_out"], data["scenes"][1]["transition_in"]]:
        transition.update(character_policy="single_visible", match_action=None)
    with pytest.raises(ValueError, match="only one scene"):
        compiler.compile(Episode.model_validate(data))
    original = store.read("registry/templates/scene.synthetic.train/1.0.json")
    template = original.model_dump(mode="json")
    template.update(id="scene.environment", channels=[])
    template["slots"] = [s for s in template["slots"] if s["kind"] != "character"]
    store.save_draft(SceneTemplate.model_validate(template), expected_revision=None)
    data["scenes"][1]["template"]["id"] = "scene.environment"
    data["actions"] = [a for a in data["actions"] if a["scene_id"] != "city"]
    assert compiler.compile(Episode.model_validate(data)).episode.scenes[1].id == "city"


@pytest.mark.parametrize("defect", ["missing-track", "outside-scene", "notebook", "duplicate"])
def test_story_contract_rejects_dangling_intent(story, defect):
    _, _, episode = story
    data = episode.model_dump(mode="json")
    if defect == "missing-track":
        data["beats"][0]["music_placements"] = ["missing"]
    elif defect == "outside-scene":
        data["beats"][0]["end_frame"] = 200
    elif defect == "notebook":
        data["continuity"]["objects"] = []
    else:
        data["beats"].append(copy.deepcopy(data["beats"][0]))
    with pytest.raises(ValueError):
        Episode.model_validate(data)


def test_incomplete_story_is_reported_without_invented_creative_approval(story):
    _, compiler, episode = story
    data = episode.model_dump(mode="json")
    data["beats"] = []
    data["continuity"] = {}
    for scene in data["scenes"]:
        scene["purpose"] = None
    report = inspect_story(compiler.compile(Episode.model_validate(data)))
    assert {issue.code for issue in report.issues} == {
        "scene_purpose_missing",
        "music_boundary_purpose_missing",
        "notebook_object_missing",
    }
    assert b'"beats"' not in canonical_bytes(Episode.model_validate(data))
    with pytest.raises(ValueError, match="authored transition purpose"):
        Transition(kind="overlap", overlap_frames=2, character_policy="single_visible")
    with pytest.raises(ValueError, match="duration"):
        Transition(kind="overlap", overlap_frames=1, character_policy="single_visible", note="Fade")


def test_scene_override_is_checked_in_its_active_scope(story):
    _, compiler, episode = story
    data = episode.model_dump(mode="json")
    global_curve = data["curves"][0]
    data["curves"].append(
        {
            **copy.deepcopy(global_curve),
            "scope": "city",
            "keys": [
                {"frame": 144, "value": 0},
                {"frame": 150, "value": 120},
            ],
        }
    )
    global_curve["limits"]["maximum"] = 10000
    # Outside the outgoing scene; the incoming scene overrides this global value.
    global_curve["keys"][-1]["value"] = 10000
    assert compiler.compile(Episode.model_validate(data)).episode.duration_frames == 300
