import json
import shutil
import wave

import pytest
from PIL import Image

from tabi.cli.main import main
from tabi.core.assets import AssetError, AssetService
from tabi.core.assets.probe import probe_media
from tabi.core.models.assets import Provenance
from tabi.core.models.base import AssetRef, FrameRate, MediaPath
from tabi.core.models.registry import ImportRequest
from tabi.core.persistence import ProjectStore, StorageError, document_path


@pytest.fixture
def setup(tmp_path):
    source = tmp_path / "Marco's 東京 originals"
    source.mkdir()
    image = source / "紫 星.png"
    Image.new("RGBA", (80, 40), (120, 40, 200, 128)).save(image)
    store = ProjectStore.initialize(tmp_path / "My 日本語 project", "Asset guard test")
    service = AssetService(store, roots={"originals": source})
    return service, image


def request(image, **changes):
    return ImportRequest(
        **{
            "id": "test.source",
            "version": "1.0",
            "kind": "still",
            "paths": [MediaPath(root_id="originals", path=image.name)],
            "provenance": Provenance(origin="synthetic", notes="Test-owned geometry"),
            **changes,
        }
    )


def ref(asset):
    return AssetRef(id=asset.id, version=asset.version)


def test_copy_preserves_original_and_reopens_with_exact_hash(setup):
    service, image = setup
    original = image.read_bytes()
    asset = service.import_asset(request(image))
    copied = service.resolve(asset.files[0].location)
    assert copied.read_bytes() == original == image.read_bytes()
    assert asset.source.root_id == "originals"
    assert asset.provenance.commercial_use == "pending"
    assert asset.approval.status == "draft"
    reopened = AssetService(ProjectStore(service.store.root))
    assert reopened.list_assets() == [asset]
    health = reopened.check(ref(asset))
    assert health.media_valid and not health.source_available
    assert not health.approval_valid and not health.publication_ready
    image.write_bytes(b"source edited after import")
    assert reopened.check(ref(asset)).media_valid
    copied.write_bytes(b"corrupt managed copy")
    health = reopened.check(ref(asset))
    assert not health.media_valid and health.files[0].status == "changed"
    with pytest.raises(AssetError):
        reopened.require_valid(ref(asset))


def test_link_missing_drive_and_relink_by_hash_never_rewrites_old_version(setup, tmp_path):
    service, image = setup
    asset = service.import_asset(request(image, mode="link"))
    old_bytes = (service.store.root / document_path(asset)).read_bytes()
    moved = tmp_path / "Relocated 東京"
    moved.mkdir()
    shutil.move(image, moved / image.name)
    assert service.check(ref(asset)).files[0].status == "missing"
    assert AssetService(service.store).check(ref(asset)).files[0].status == "inaccessible"
    service.roots["new"] = moved
    linked = service.relink(
        ref(asset), version="1.1", paths=[MediaPath(root_id="new", path=image.name)]
    )
    assert service.check(ref(linked)).media_valid
    assert linked.approval.status == "draft" and linked.files[0].sha256 == asset.files[0].sha256
    assert (service.store.root / document_path(asset)).read_bytes() == old_bytes
    (moved / image.name).write_bytes(b"different source")
    with pytest.raises(AssetError, match="hashes"):
        service.relink(ref(asset), version="1.2", paths=[MediaPath(root_id="new", path=image.name)])
    assert not (service.store.root / "registry/assets/test.source/1.2.json").exists()


def test_approval_requires_reviewed_hash_rights_and_current_bytes(setup):
    service, image = setup
    # A temporary test record exercises explicit review. This is not a real art approval.
    asset = service.import_asset(
        request(
            image,
            provenance=Provenance(
                origin="user_supplied",
                creator="Synthetic test reviewer",
                commercial_use="confirmed",
                notes="Test-only approval guard; destroyed with temporary project",
            ),
        )
    )
    with pytest.raises(AssetError, match="stale"):
        service.approve(ref(asset), expected_hash="0" * 64, reviewer="Test", note="Test")
    approved = service.approve(
        ref(asset),
        expected_hash=asset.approval_hash,
        reviewer="Synthetic test reviewer",
        note="Temporary test only",
    )
    saved = (service.store.root / document_path(approved)).read_bytes()
    assert service.check(ref(asset)).publication_ready
    service.resolve(asset.files[0].location).write_bytes(b"edited content")
    assert not service.check(ref(asset)).approval_valid
    assert not service.check(ref(asset)).publication_ready
    assert (service.store.root / document_path(approved)).read_bytes() == saved
    with pytest.raises(AssetError):
        service.require_valid(ref(asset), production=True)


@pytest.mark.parametrize(
    "provenance", [Provenance(origin="synthetic"), Provenance(origin="user_supplied")]
)
def test_synthetic_and_pending_rights_cannot_be_approved(setup, provenance):
    service, image = setup
    asset = service.import_asset(request(image, provenance=provenance))
    with pytest.raises(AssetError):
        service.approve(ref(asset), expected_hash=asset.approval_hash, reviewer="Test", note="Test")
    assert service.load(ref(asset)).approval.status == "draft"


def test_image_proxy_new_version_retains_sources_and_alpha(setup):
    service, image = setup
    asset = service.import_asset(request(image))
    source_bytes = image.read_bytes()
    proxy = service.image_proxies(ref(asset), version="1.1", max_edge=40)
    assert proxy.files == asset.files and proxy.approval.status == "draft"
    assert service.load(ref(asset)).proxies == []
    assert service.check(ref(proxy)).proxies[0].status == "ok"
    with Image.open(service.resolve(proxy.proxies[0].location)) as decoded:
        assert decoded.size == (40, 20) and decoded.getpixel((10, 10))[3] == 128
    assert image.read_bytes() == source_bytes
    assert service.resolve(asset.files[0].location).read_bytes() == source_bytes
    with pytest.raises(AssetError, match="newer"):
        service.image_proxies(ref(asset), version="1.0")


def test_interrupted_import_and_version_conflict_clean_only_owned_staging(setup, monkeypatch):
    service, image = setup
    source_bytes = image.read_bytes()
    asset = service.import_asset(request(image))
    sources_before = sorted(p for p in (service.store.root / "sources").rglob("*") if p.is_file())
    with pytest.raises(AssetError, match="exists"):
        service.import_asset(request(image))
    assert (
        sorted(p for p in (service.store.root / "sources").rglob("*") if p.is_file())
        == sources_before
    )
    write = service.store._atomic_write

    def fail_registry(path, *args, **kwargs):
        if path.startswith("registry/"):
            raise OSError("synthetic disk full")
        return write(path, *args, **kwargs)

    monkeypatch.setattr(service.store, "_atomic_write", fail_registry)
    with pytest.raises(OSError, match="disk full"):
        service.import_asset(request(image, version="1.1"))
    assert not list(service.store.root.glob(".tabi-import-*"))
    assert (
        sorted(p for p in (service.store.root / "sources").rglob("*") if p.is_file())
        == sources_before
    )
    assert image.read_bytes() == source_bytes
    assert service.check(ref(asset)).media_valid


def test_sequence_order_timing_and_shape_are_explicit(setup):
    service, image = setup
    other = image.with_name("second.png")
    Image.new("RGBA", (80, 40), (0, 200, 40, 255)).save(other)
    locations = [MediaPath(root_id="originals", path=p.name) for p in [other, image]]
    with pytest.raises(ValueError, match="fps"):
        service.import_asset(request(image, kind="sequence", paths=locations))
    sequence = service.import_asset(
        request(image, kind="sequence", paths=locations, fps=FrameRate(num=25, den=1))
    )
    assert sequence.probe.frame_count == 2 and sequence.probe.fps.num == 25
    with Image.open(service.resolve(sequence.files[0].location)) as first:
        assert first.getpixel((0, 0)) == (0, 200, 40, 255)
    Image.new("RGBA", (81, 40)).save(other)
    with pytest.raises(ValueError, match="share canvas"):
        service.import_asset(
            request(
                image, kind="sequence", paths=locations, fps=FrameRate(num=25, den=1), version="1.1"
            )
        )


def test_corrupt_mask_escape_and_nonfile_are_rejected(setup, tmp_path):
    service, image = setup
    with pytest.raises(ValueError, match="grayscale"):
        service.import_asset(request(image, kind="mask"))
    outside = tmp_path / "outside.png"
    image.rename(outside)
    image.symlink_to(outside)
    with pytest.raises(StorageError, match="escapes"):
        service.import_asset(request(image))
    image.unlink()
    image.write_bytes(b"invalid PNG")
    with pytest.raises(OSError):
        service.import_asset(request(image))


def test_wav_probe_uses_exact_samples_and_rejects_truncation(tmp_path):
    path = tmp_path / "samples.wav"
    with wave.open(str(path), "wb") as audio:
        audio.setparams((2, 2, 48000, 0, "NONE", "not compressed"))
        audio.writeframes(b"\0" * 4 * 12345)
    probe = probe_media([path], "audio", fps=None, ffmpeg="unused", ffprobe="unused")
    assert probe.duration_samples == 12345 and probe.channels == 2
    path.write_bytes(path.read_bytes()[:-4])
    with pytest.raises(ValueError, match="truncated"):
        probe_media([path], "audio", fps=None, ffmpeg="unused", ffprobe="unused")


def test_cli_import_check_reopen_with_explicit_roots(setup, tmp_path, capsys):
    service, image = setup
    request_path = tmp_path / "import.json"
    request_path.write_text(request(image).model_dump_json())
    assert (
        main(
            [
                "asset",
                "import",
                str(service.store.root),
                str(request_path),
                "--root",
                f"originals={image.parent}",
            ]
        )
        == 0
    )
    imported = json.loads(capsys.readouterr().out)
    assert imported["provenance"]["origin"] == "synthetic"
    assert main(["asset", "check", str(service.store.root), "test.source", "1.0"]) == 0
    assert json.loads(capsys.readouterr().out)["media_valid"]
