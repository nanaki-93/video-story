import pytest
from PIL import Image

from tabi.core.assets import AssetService
from tabi.core.documents import validate_data
from tabi.core.editor import EditorService, EditRequest
from tabi.core.fixtures import generate_fixtures
from tabi.core.models import ActionPack, Asset
from tabi.core.models.base import AssetRef, canonical_bytes
from tabi.core.persistence import ProjectStore
from tabi.core.timeline.compiler import ActionCompiler, CompileError
from tabi.core.timeline.state import state_parts


@pytest.fixture
def activity(tmp_path):
    root = tmp_path / "Activities 東京"
    generate_fixtures(root, profile="activities")
    return EditorService(AssetService(ProjectStore(root)))


def test_activity_transitions_props_and_authored_pixel_endpoints(activity):
    episode = activity.episode("episode.synthetic")
    snapshot = ActionCompiler(activity.assets).compile(episode)
    actions = [e for e in snapshot.schedule if e.type == "action"]
    assert len(actions) == 10
    for frame, held in ((54, "cup"), (138, "book"), (222, None), (300, None)):
        _, props = state_parts(episode.scenes[0].initial_state, actions, [], "cafe", frame)
        assert props == {p: "hand" if p == held else "table" for p in ("cup", "book")}

    def pixels(name, n):
        path = activity.store.root / "assets" / f"fixture.activity.blue.{name}" / f"{n:06}.png"
        with Image.open(path) as image:
            return image.tobytes()

    for name in ("sip", "read", "sleep"):
        assert pixels(name + ".entry", 0) == pixels("idle", 0) == pixels(name + ".exit", 5)
        assert pixels(name + ".entry", 5) == pixels(name, 0) == pixels(name, 11)
        assert pixels(name, 0) == pixels(name + ".exit", 0)
    invalid = episode.model_dump(mode="json")
    invalid["scenes"][0]["initial_state"]["props"]["cup"] = "shelf"
    with pytest.raises(CompileError, match="prop"):
        ActionCompiler(activity.assets).compile(validate_data(invalid))


def test_switch_pack_outfit_and_version_is_atomic_and_preserves_source(activity):
    before = activity.episode("episode.synthetic")
    pack_path = "registry/actions/pack.synthetic.activities.blue/1.0.json"
    source_path = "registry/assets/fixture.activity.blue.idle/1.0.json"
    original = {path: activity.store._read_bytes(path) for path in (pack_path, source_path)}
    replacement = activity.store.read("registry/actions/pack.synthetic.activities.amber/1.0.json")
    new_version = replacement.model_copy(update={"version": "1.1"})
    activity.store.save_draft(new_version, expected_revision=None)
    saved = activity.edit(
        before.id,
        EditRequest(
            expected_revision=0,
            command={
                "kind": "change_pack",
                "scene_id": "cafe",
                "pack": {"id": replacement.id, "version": "1.1"},
            },
        ),
    )
    assert saved.scenes[0].character_outfit_id == "fixture.outfit.amber"
    assert all(a.pack.version == "1.1" for a in saved.actions)
    assert [(a.start_frame, a.end_frame) for a in saved.actions] == [
        (a.start_frame, a.end_frame) for a in before.actions
    ]
    for path, content in original.items():
        assert activity.store._read_bytes(path) == content
    last_good = canonical_bytes(saved)
    with pytest.raises(ValueError, match="lacks action"):
        activity.edit(
            before.id,
            EditRequest(
                expected_revision=1,
                command={
                    "kind": "change_pack",
                    "scene_id": "cafe",
                    "pack": {"id": "pack.synthetic.cafe", "version": "1.0"},
                },
            ),
        )
    assert canonical_bytes(activity.episode(before.id)) == last_good


def test_camera_and_outfit_mismatches_reject_without_implicit_conversion(activity):
    episode = activity.episode("episode.synthetic")
    bad = episode.model_dump(mode="json")
    bad["actions"][0]["pack"]["id"] = "pack.synthetic.activities.amber"
    with pytest.raises(CompileError, match="outfit"):
        ActionCompiler(activity.assets).compile(validate_data(bad))
    path = "registry/assets/fixture.activity.blue.sip/1.0.json"
    asset = activity.store.read(path)
    for compatibility, message in (
        ({"cameras": ["other.camera"]}, "camera"),
        ({"outfits": ["other.outfit"]}, "outfit"),
    ):
        values = asset.model_dump(mode="json")
        values["compatibility"].update(compatibility)
        current = activity.store.read(path)
        values["revision"] = current.revision
        activity.store.save_draft(Asset.model_validate(values), expected_revision=current.revision)
        with pytest.raises(CompileError, match=message):
            ActionCompiler(activity.assets).compile(episode)


def test_unspecified_outfit_preserves_legacy_document_hashes(activity):
    pack = activity.store.read("registry/actions/pack.synthetic/1.0.json")
    asset = activity.assets.load(AssetRef(id="fixture.idle", version="1.0"))
    assert "outfit_id" not in pack.model_dump(mode="json")
    assert "outfits" not in asset.model_dump(mode="json")["compatibility"]
    old_pack = pack.model_dump(mode="json")
    assert canonical_bytes(ActionPack.model_validate(old_pack)) == canonical_bytes(old_pack)
