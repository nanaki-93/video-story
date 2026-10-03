import pytest

from tabi.core.assets import AssetService
from tabi.core.editor import EditorService, EditRequest
from tabi.core.fixtures import generate_fixtures
from tabi.core.models.base import AssetRef, canonical_bytes
from tabi.core.persistence import ProjectStore
from tabi.core.timeline.compiler import ActionCompiler, CompileError


def test_cafe_reuses_editor_and_renderer_contract_with_explicit_pack(tmp_path):
    root = tmp_path / "Café 東京"
    generate_fixtures(root, profile="cafe")
    assets = AssetService(ProjectStore(root))
    editor = EditorService(assets)
    before = editor.episode("episode.synthetic")
    source = canonical_bytes(assets.load(AssetRef(id="fixture.idle", version="1.0")))
    scene = before.scenes[0].model_dump(mode="json")
    scene["purpose"] = "Watch the street from a stationary café table."
    saved = editor.edit(
        before.id,
        EditRequest(expected_revision=0, command={"kind": "scene", "scene": scene}),
    )
    compiled = ActionCompiler(assets, purpose="synthetic_test").compile(saved)
    assert saved.revision == 1 and compiled.episode.scenes[0].id == "cafe"
    assert {e.pack.id for e in compiled.schedule if e.type == "action"} == {"pack.synthetic.cafe"}
    assert source == canonical_bytes(assets.load(AssetRef(id="fixture.idle", version="1.0")))
    # A train-compatible pack cannot silently fit a café, even when camera/media are shared.
    bad = saved.model_copy(deep=True)
    bad.actions[0] = bad.actions[0].model_copy(
        update={"pack": AssetRef(id="pack.synthetic", version="1.0")}
    )
    with pytest.raises(CompileError, match="camera/template is incompatible"):
        ActionCompiler(assets).compile(bad)
    assert editor.episode(saved.id) == saved


def test_cafe_generation_is_repeatable_and_remains_synthetic(tmp_path):
    first = generate_fixtures(tmp_path / "one", profile="cafe")
    second = generate_fixtures(tmp_path / "two", profile="cafe")
    assert first == second
    assets = AssetService(ProjectStore(tmp_path / "one"))
    for entry in EditorService(assets).templates():
        assert entry.approval.status == "draft"
    with pytest.raises(CompileError, match="approval"):
        ActionCompiler(assets, purpose="production").compile(
            EditorService(assets).episode("episode.synthetic")
        )
