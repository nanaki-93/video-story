import wave

import pytest
from PIL import Image

from tabi.core import fixtures
from tabi.core.documents import read_document
from tabi.core.models import ActionPack, Asset, Episode, SceneTemplate
from tabi.core.models.base import canonical_bytes
from tabi.core.persistence import StorageError
from tabi.core.toolchain import file_hash


def test_fixture_pack_is_portable_reproducible_and_fully_hashed(tmp_path):
    first, second = tmp_path / "Marco's 東京 fixtures", tmp_path / "second"
    a, b = fixtures.generate_fixtures(first), fixtures.generate_fixtures(second)
    assert a == b and (first / "fixtures.json").read_bytes() == canonical_bytes(b)
    assert 50 < len(a.files) < 100
    assert sum(f.size_bytes for f in a.files) < 3_000_000
    for entry in a.files:
        path = first / entry.location.path
        assert path.stat().st_size == entry.size_bytes and file_hash(path) == entry.sha256
        if path.suffix == ".json":
            read_document(path)
    assets = [read_document(p) for p in (first / "registry/assets").rglob("*.json")]
    assert len(assets) == 14
    assert all(
        isinstance(a, Asset) and a.provenance.origin == "synthetic" and a.approval.status == "draft"
        for a in assets
    )
    episode = read_document(first / a.episode)
    assert isinstance(episode, Episode) and episode.duration_frames == 300
    assert episode.fps.sample_at(episode.duration_frames) == 480000
    refs = {(asset.id, asset.version) for asset in assets}
    template = read_document(first / "registry/templates/scene.synthetic.train/1.0.json")
    pack = read_document(first / "registry/actions/pack.synthetic/1.0.json")
    assert isinstance(template, SceneTemplate) and isinstance(pack, ActionPack)
    assert all((a.clip.id, a.clip.version) in refs for a in pack.actions)
    assert episode.references().issubset(
        refs | {(template.id, template.version), (pack.id, pack.version)}
    )
    with wave.open(str(first / "audio/fixture.tone.wav")) as audio:
        assert (audio.getnframes(), audio.getframerate(), audio.getnchannels()) == (
            480000,
            48000,
            2,
        )
    with wave.open(str(first / "audio/fixture.silence.wav")) as silence:
        assert not any(silence.readframes(48000))


def test_fixture_loop_transition_alpha_mask_and_tile_endpoints(tmp_path):
    root = tmp_path / "fixtures"
    fixtures.generate_fixtures(root)

    def pixels(name, n):
        with Image.open(root / "assets" / f"fixture.{name}" / f"{n:06}.png") as im:
            assert im.mode == "RGBA"
            return im.tobytes()

    assert pixels("idle", 0) == pixels("idle", 11) == pixels("entry", 0) == pixels("exit", 5)
    assert pixels("observe", 0) == pixels("observe", 11) == pixels("entry", 5) == pixels("exit", 0)
    for n in (0, 5):
        with Image.open(root / "assets/fixture.blink" / f"{n:06}.png") as im:
            assert im.getchannel("A").getextrema() == (0, 0)
    with Image.open(root / "assets/fixture.window/image.png") as mask:
        assert mask.mode == "L" and mask.getpixel((100, 100)) == 255
        assert mask.getpixel((5, 100)) == 0
    for layer in ("far", "mid", "near"):
        with Image.open(root / f"assets/fixture.{layer}/image.png") as strip:
            assert (
                strip.crop((0, 0, 640, 360)).tobytes() == strip.crop((640, 0, 1280, 360)).tobytes()
            )


def test_generation_never_replaces_existing_content(tmp_path):
    root = tmp_path / "existing"
    root.mkdir()
    source = root / "source.txt"
    source.write_text("preserve original")
    with pytest.raises(StorageError, match="already exists"):
        fixtures.generate_fixtures(root)
    assert source.read_text() == "preserve original"


def test_failed_fixture_generation_cleans_only_its_own_staging(tmp_path, monkeypatch):
    root = tmp_path / "new"

    def fail(path, **_):
        path.mkdir()
        (path / "partial").write_text("synthetic")
        raise OSError("synthetic interrupted generation")

    monkeypatch.setattr(fixtures, "_populate", fail)
    with pytest.raises(OSError, match="interrupted"):
        fixtures.generate_fixtures(root)
    assert not root.exists() and not list(tmp_path.iterdir())
