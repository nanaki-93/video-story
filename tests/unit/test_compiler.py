import json

import pytest

from tabi.core.assets import AssetService
from tabi.core.fixtures import generate_fixtures
from tabi.core.models import ActionPack, Episode
from tabi.core.models.base import canonical_bytes
from tabi.core.models.production import ScheduledAction
from tabi.core.persistence import ProjectStore
from tabi.core.timeline.compiler import ActionCompiler, CompileError, state_at


@pytest.fixture
def fixture(tmp_path):
    root = tmp_path / "compiler's 東京 project"
    generate_fixtures(root)
    store = ProjectStore(root)
    compiler = ActionCompiler(AssetService(store), purpose="synthetic_test")
    episode = store.read("episodes/episode.synthetic.json")
    return store, compiler, episode


def edit_pack(store, mutate):
    path = "registry/actions/pack.synthetic/1.0.json"
    original = store.read(path)
    data = original.model_dump(mode="json")
    mutate(data)
    store.save_draft(ActionPack.model_validate(data), expected_revision=original.revision)


def test_explicit_fixture_compiles_identically_and_blink_does_not_restart_body(fixture):
    store, compiler, episode = fixture
    snapshot = compiler.compile(episode)
    assert canonical_bytes(snapshot) == canonical_bytes(compiler.compile(episode))
    assert len(snapshot.schedule) == 8 and len(snapshot.locked_assets) == 15
    assert snapshot.episode.scenes[0].final_state.travel_distance_px == 780
    for frame in [42, 35, 41, 36, 37]:
        state = state_at(snapshot, "train", frame)
        body = next(a for a in state["actions"] if a["channel"] == "body")
        assert body["source_frame"] == frame % 12
        assert any(a["channel"] == "face" for a in state["actions"]) == (36 <= frame < 42)
    assert state_at(snapshot, "train", 89)["body_pose"] == "idle"
    assert state_at(snapshot, "train", 90)["body_pose"] == "observing"
    assert state_at(snapshot, "train", 216)["body_pose"] == "idle"
    digest = store.save_snapshot(snapshot)
    assert store.read_snapshot(digest) == snapshot


def test_loop_request_expands_entry_hold_exit_without_retiming(fixture):
    _, compiler, episode = fixture
    data = episode.model_dump(mode="json")
    # Replace the three explicit middle requests with one observing window.
    requests = [request for request in data["actions"] if request["channel"] == "body"]
    middle = {**requests[2], "start_frame": 84, "end_frame": 216}
    data["actions"] = [requests[0], middle, requests[-1]]
    plan = compiler.compile(Episode.model_validate(data))
    body = [event for event in plan.schedule if isinstance(event, ScheduledAction)]
    assert [(a.action_id, a.start_frame, a.end_frame) for a in body] == [
        ("fixture.idle", 0, 84),
        ("fixture.entry", 84, 90),
        ("fixture.observe", 90, 210),
        ("fixture.exit", 210, 216),
        ("fixture.idle", 216, 300),
    ]
    middle["end_frame"] = 217
    data["actions"][-1]["start_frame"] = 217
    with pytest.raises(CompileError, match="whole"):
        compiler.compile(Episode.model_validate(data))


def test_missing_transition_and_props_fail_with_actionable_diagnostics(fixture):
    store, compiler, episode = fixture
    data = episode.model_dump(mode="json")
    body = [request for request in data["actions"] if request["channel"] == "body"]
    data["actions"] = [body[0], {**body[2], "start_frame": 84, "end_frame": 216}, body[-1]]
    edit_pack(store, lambda pack: pack["actions"].pop(1))
    with pytest.raises(CompileError, match="missing compatible transition idle"):
        compiler.compile(Episode.model_validate(data))
    edit_pack(store, lambda pack: pack["actions"][0].update(requires_props={"cup": "hand"}))
    with pytest.raises(CompileError, match="requires props"):
        compiler.compile(Episode.model_validate({**data, "actions": [body[0]]}))


def test_one_shot_runs_once_and_never_stretches(fixture):
    _, compiler, episode = fixture
    data = episode.model_dump(mode="json")
    next(a for a in data["actions"] if a["action_id"] == "fixture.entry")["repeat"] = "loop_to_fill"
    with pytest.raises(CompileError, match="one-shot"):
        compiler.compile(Episode.model_validate(data))


@pytest.mark.parametrize("defect", ["occupied", "pose", "fps", "camera"])
def test_pack_channel_pose_rate_and_camera_compatibility(fixture, defect):
    store, compiler, episode = fixture

    def change(pack):
        if defect == "occupied":
            pack["actions"][0]["occupies_channels"].append("face")
        elif defect == "pose":
            pack["actions"][-1]["compatible_body_poses"] = ["observing"]
        elif defect == "fps":
            pack["fps"] = {"num": 25, "den": 1}
        else:
            pack["camera_id"] = "other.camera"

    edit_pack(store, change)
    with pytest.raises(
        CompileError,
        match={"occupied": "occupies", "pose": "incompatible", "fps": "fps", "camera": "camera"}[
            defect
        ],
    ):
        compiler.compile(episode)


def test_props_commit_at_exact_action_end_and_can_be_explicitly_moved(fixture):
    store, compiler, episode = fixture
    edit_pack(
        store,
        lambda pack: pack["actions"][1].update(
            requires_props={"cup": "table"}, resulting_props={"cup": "hand"}
        ),
    )
    data = episode.model_dump(mode="json")
    data["scenes"][0]["initial_state"]["props"] = {"cup": "table"}
    data["scenes"][0]["final_state"]["props"] = {"cup": "table"}
    data["events"].append(
        {
            "type": "prop",
            "id": "return.cup",
            "scene_id": "train",
            "frame": 216,
            "object_id": "cup",
            "location": "table",
        }
    )
    plan = compiler.compile(Episode.model_validate(data))
    assert state_at(plan, "train", 89)["props"]["cup"] == "table"
    assert state_at(plan, "train", 90)["props"]["cup"] == "hand"
    assert state_at(plan, "train", 215)["props"]["cup"] == "hand"
    assert state_at(plan, "train", 216)["props"]["cup"] == "table"


def two_scenes(episode):
    data = episode.model_dump(mode="json")
    data.update(actions=[], tracks=[], events=[], curves=[])
    source = data["scenes"][0]
    source.update(end_frame=144, final_state=None, curves=[], events=[])
    second = json.loads(json.dumps(source))
    second.update(id="second", start_frame=144, end_frame=300)
    data["scenes"] = [source, second]
    for i, scene in enumerate(data["scenes"]):
        data["actions"].append(
            {
                "id": f"idle.{i}",
                "scene_id": scene["id"],
                "pack": {"id": "pack.synthetic", "version": "1.0"},
                "action_id": "fixture.idle",
                "version": "1.0",
                "channel": "body",
                "repeat": "loop_to_fill",
                "start_frame": scene["start_frame"],
                "end_frame": scene["end_frame"],
            }
        )
    return data


def test_scene_cuts_preserve_props_or_require_deliberate_reset(fixture):
    _, compiler, episode = fixture
    data = two_scenes(episode)
    data["scenes"][0]["initial_state"]["props"] = {"cup": "table"}
    with pytest.raises(CompileError, match="deliberate_reset"):
        compiler.compile(Episode.model_validate(data))
    data["scenes"][1]["initial_state"]["props"] = {"cup": "table"}
    plan = compiler.compile(Episode.model_validate(data))
    assert state_at(plan, "second", 144)["props"] == {"cup": "table"}
    data["scenes"][1]["continuity"] = "deliberate_reset"
    data["scenes"][1]["initial_state"]["props"] = {"book": "table"}
    assert state_at(compiler.compile(Episode.model_validate(data)), "second", 144)["props"] == {
        "book": "table"
    }


def test_production_rejects_unapproved_fixture_pack_and_changed_media(fixture):
    store, compiler, episode = fixture
    with pytest.raises(CompileError, match="approval"):
        ActionCompiler(AssetService(store), purpose="production").compile(episode)
    path = store.root / "assets/fixture.idle/000000.png"
    path.write_bytes(b"altered frame")
    with pytest.raises(ValueError, match="missing, changed"):
        compiler.compile(episode)


def test_declared_final_state_must_match_actual_travel_and_props(fixture):
    _, compiler, episode = fixture
    data = episode.model_dump(mode="json")
    data["scenes"][0]["final_state"]["travel_distance_px"] = 0
    with pytest.raises(CompileError, match="final state"):
        compiler.compile(Episode.model_validate(data))
