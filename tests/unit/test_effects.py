import pytest

from tabi.core.assets import AssetService
from tabi.core.fixtures import generate_fixtures
from tabi.core.models import Episode, SceneTemplate
from tabi.core.models.base import canonical_bytes
from tabi.core.persistence import ProjectStore
from tabi.core.timeline.compiler import ActionCompiler
from tabi.core.timeline.curves import Timeline
from tabi.core.timeline.effects import validate_effects


def test_effect_fixture_is_reproducible_and_invalid_strength_or_phase_fails(tmp_path):
    first, second = tmp_path / "first", tmp_path / "second"
    a, b = generate_fixtures(first, profile="effects"), generate_fixtures(second, profile="effects")
    assert a == b and len(a.files) == 86
    assert all(
        (first / item.location.path).read_bytes() == (second / item.location.path).read_bytes()
        for item in a.files
    )
    assets = AssetService(ProjectStore(first))
    episode = assets.store.read("episodes/episode.synthetic.json")
    compiler = ActionCompiler(assets, purpose="synthetic_test")
    assert len(compiler.compile(episode).locked_assets) == 18
    data = episode.model_dump()
    rain = next(c for c in data["curves"] if c["target"] == "rain_amount")
    rain["limits"]["maximum"] = 1.0
    rain["keys"][2]["value"] = 0.8
    with pytest.raises(ValueError, match="limits"):
        compiler.compile(Episode.model_validate(data))
    invalid = Episode.model_validate(data)
    template = assets.store.read("registry/templates/scene.synthetic.train/1.0.json")
    with pytest.raises(ValueError, match="limits"):
        validate_effects(invalid.scenes[0], template, Timeline(invalid), compiler.resolve)
    data = episode.model_dump()
    data["scenes"][0]["initial_state"]["weather_phase_frame"] = 1
    with pytest.raises(ValueError, match="phase origin"):
        compiler.compile(Episode.model_validate(data))
    data = episode.model_dump()
    data["curves"][-1]["unit"] = "degrees"
    with pytest.raises(ValueError, match="fraction"):
        compiler.compile(Episode.model_validate(data))


def test_masks_capabilities_loops_and_temporal_history_cannot_be_invented(tmp_path):
    root = tmp_path / "effects"
    generate_fixtures(root, profile="effects")
    assets = AssetService(ProjectStore(root))
    template = assets.store.read("registry/templates/scene.synthetic.train/1.0.json")
    for field, value, pattern in [("mask", None, "mask"), ("effect", None, "specification")]:
        data = template.model_dump()
        next(s for s in data["slots"] if s["id"] == "rain")[field] = value
        with pytest.raises(ValueError, match=pattern):
            SceneTemplate.model_validate(data)
    data = template.model_dump()
    next(s for s in data["slots"] if s["id"] == "rain")["effect"]["kind"] = "temporal_blur"
    with pytest.raises(ValueError):
        SceneTemplate.model_validate(data)
    data = template.model_dump()
    next(s for s in data["slots"] if s["id"] == "rain")["effect"]["loop"]["end_frame"] = 13
    assets.store.save_draft(SceneTemplate.model_validate(data), expected_revision=template.revision)
    with pytest.raises(ValueError, match="valid PNG"):
        ActionCompiler(assets, purpose="synthetic_test").compile(
            assets.store.read("episodes/episode.synthetic.json")
        )


def test_absent_effect_fields_preserve_prior_template_identity(tmp_path):
    root = tmp_path / "core"
    generate_fixtures(root)
    path = root / "registry/templates/scene.synthetic.train/1.0.json"
    raw = path.read_bytes()
    assert b'"effect"' not in raw
    assert canonical_bytes(SceneTemplate.model_validate_json(raw)) == raw
