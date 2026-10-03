import hashlib
from pathlib import Path
from types import SimpleNamespace

import pytest
from PIL import Image

from tabi.core.assets import AssetService
from tabi.core.config import load_settings
from tabi.core.fixtures import generate_fixtures
from tabi.core.models import Asset
from tabi.core.models.base import AssetRef
from tabi.core.persistence import ProjectStore
from tabi.core.render.backend import RenderError
from tabi.core.render.ffmpeg import FFmpegRenderer
from tabi.core.render.normalize import ImageNormalizer
from tabi.core.timeline.compiler import ActionCompiler


def test_premultiplied_input_becomes_straight_without_changing_source(tmp_path):
    store = ProjectStore.initialize(tmp_path / "project", "Synthetic alpha test")
    path = store.root / "assets" / "premultiplied.png"
    source = Image.new("RGBA", (2, 1))
    source.putdata([(50, 20, 5, 128), (0, 0, 0, 0)])
    source.save(path)
    original = path.read_bytes()
    record = Asset.model_validate(
        {
            "schema_version": "1.0",
            "document_type": "asset",
            "id": "alpha.test",
            "version": "1.0",
            "kind": "still",
            "source": {"path": "assets/premultiplied.png"},
            "files": [
                {
                    "location": {"path": "assets/premultiplied.png"},
                    "sha256": hashlib.sha256(original).hexdigest(),
                    "size_bytes": len(original),
                }
            ],
            "probe": {
                "canvas": {"width": 2, "height": 1},
                "alpha_mode": "premultiplied",
                "color_space": "srgb",
            },
            "provenance": {"origin": "synthetic"},
        }
    )
    registry = SimpleNamespace(
        assets=AssetService(store), snapshot=SimpleNamespace(purpose="synthetic_test")
    )
    normalizer = ImageNormalizer(registry, tmp_path / "normalized")
    prepared = normalizer.prepare(record)
    with Image.open(prepared) as image:
        assert image.getpixel((0, 0)) == (99, 39, 9, 128)
        assert image.getpixel((1, 0)) == (0, 0, 0, 0)
    assert normalizer.prepare(record) == prepared and len(normalizer.prepared) == 1
    assert path.read_bytes() == original


def test_unknown_color_is_preview_only_and_mask_values_remain_exact(tmp_path):
    root = tmp_path / "fixtures"
    generate_fixtures(root)
    service = AssetService(ProjectStore(root))
    registry = SimpleNamespace(assets=service, snapshot=SimpleNamespace(purpose="production"))
    normalizer = ImageNormalizer(registry, tmp_path / "normalized")
    asset = service.load(AssetRef(id="fixture.cabin", version="1.0"))
    asset = asset.model_copy(
        update={"probe": asset.probe.model_copy(update={"color_space": "unknown"})}
    )
    with pytest.raises(RenderError, match="color"):
        normalizer.prepare(asset)
    registry.snapshot.purpose = "preview"
    normalizer.prepare(asset)
    assert len(normalizer.warnings) == 1
    mask = service.load(AssetRef(id="fixture.window", version="1.0"))
    prepared = normalizer.prepare(mask)
    with (
        Image.open(prepared) as image,
        Image.open(service.resolve(mask.files[0].location)) as source,
    ):
        assert image.mode == "L" and image.tobytes() == source.tobytes()


def test_invalid_ranges_fail_before_creating_outputs(tmp_path):
    root = tmp_path / "fixture"
    generate_fixtures(root)
    service = AssetService(ProjectStore(root))
    episode = service.store.read("episodes/episode.synthetic.json")
    snapshot = ActionCompiler(service, purpose="synthetic_test").compile(episode)
    config = load_settings(None, env={}, cwd=tmp_path, home=Path.home())
    renderer = FFmpegRenderer(service, config)
    output = tmp_path / "new directory" / "no.png"
    for frame in (-1, 300, True):
        with pytest.raises(RenderError, match="range"):
            renderer.frame(snapshot, frame, output)
    assert not output.parent.exists()
