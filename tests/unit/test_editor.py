import pytest

from tabi.core.assets import AssetService
from tabi.core.documents import DocumentError
from tabi.core.editor import EditorService, EditRequest
from tabi.core.fixtures import generate_fixtures
from tabi.core.models.base import canonical_bytes
from tabi.core.persistence import ProjectStore, RevisionConflict


@pytest.fixture
def editor(tmp_path):
    root = tmp_path / "Editor 東京"
    generate_fixtures(root)
    store = ProjectStore(root)
    return EditorService(AssetService(store))


def edit(service, revision, **command):
    return service.edit(
        "episode.synthetic",
        EditRequest.model_validate(
            {
                "expected_revision": revision,
                "command": command,
            }
        ),
    )


def test_move_action_preserves_duration_and_rejects_overlap_or_gaps_atomically(editor):
    before = editor.episode("episode.synthetic")
    action = next(a for a in before.actions if a.channel == "face")
    moved = edit(editor, 0, kind="move_action", id=action.id, start_frame=48)
    actual = next(a for a in moved.actions if a.id == action.id)
    assert actual.end_frame - actual.start_frame == action.end_frame - action.start_frame
    assert (actual.start_frame, actual.end_frame) == (48, 54)
    disk = editor.store._read_bytes("episodes/episode.synthetic.json")
    with pytest.raises(DocumentError) as invalid:
        edit(editor, 1, kind="move_action", id=action.id, start_frame=299)
    assert any("outside" in issue.message for issue in invalid.value.issues)
    body = next(a for a in moved.actions if a.channel == "body")
    with pytest.raises(DocumentError) as invalid:
        edit(editor, 1, kind="move_action", id=body.id, start_frame=1)
    assert any("overlapping" in issue.message for issue in invalid.value.issues)
    assert editor.store._read_bytes("episodes/episode.synthetic.json") == disk


def test_undo_roundtrip_is_new_revision_and_stale_tab_cannot_overwrite(editor):
    initial = editor.episode("episode.synthetic")
    saved = edit(editor, 0, kind="title", title="Authored title")
    with pytest.raises(RevisionConflict):
        edit(editor, 0, kind="title", title="Stale tab")
    restored = edit(editor, saved.revision, kind="replace", episode=initial.model_dump(mode="json"))
    assert restored.revision == 2
    assert canonical_bytes(restored.model_copy(update={"revision": 0})) == canonical_bytes(initial)
    assert list((editor.store.root / ".backups").rglob("*"))


def test_curve_notebook_and_unknown_commands_are_checked(editor):
    before = editor.episode("episode.synthetic")
    curve = before.curves[0].model_dump(mode="json")
    changed = {**curve, "keys": [{"frame": 0, "value": -10}]}
    with pytest.raises(ValueError):
        edit(editor, 0, kind="put_curve", curve=changed)
    saved = edit(
        editor,
        0,
        kind="continuity",
        continuity={
            "summary": "Synthetic notebook test",
            "objects": ["cup"],
            "object_notes": {"cup": "Remains on the table"},
            "notes": [],
        },
    )
    assert saved.continuity.object_notes == {"cup": "Remains on the table"}
    with pytest.raises(ValueError):
        edit(editor, 1, kind="invent_action", prompt="magic")
    lanes = editor.lanes(saved)
    music = next(lane for lane in lanes if lane["id"] == "music")["items"][0]
    assert music["start_frame"] == 0 and music["end_frame"] == 300
    assert "480000" in music["label"]
