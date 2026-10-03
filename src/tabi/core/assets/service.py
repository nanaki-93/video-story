"""File-backed registry. External roots come from the caller, never imported metadata."""

import hashlib
import io
import os
import shutil
import stat
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from PIL import Image, ImageCms, ImageOps

from ..documents import validate_data
from ..models import Asset, Project
from ..models.assets import Approval
from ..models.base import AssetRef, HashedFile, MediaPath, canonical_bytes, version_tuple
from ..models.portability import PortableRoots
from ..models.registry import AssetHealth, FileHealth, ImportRequest
from ..persistence import ProjectStore, StorageError, document_path, resolve_media_path
from .probe import image_probe, probe_media


class AssetError(StorageError):
    pass


def digest_file(path: Path) -> tuple[str, int]:
    # Refuse FIFOs/devices and detect ordinary concurrent source edits.
    descriptor = os.open(path, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW)
    with os.fdopen(descriptor, "rb") as stream:
        before = os.fstat(stream.fileno())
        if not stat.S_ISREG(before.st_mode):
            raise AssetError("media must be a regular file")
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
        after = os.fstat(stream.fileno())
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise AssetError("source changed while hashing; retry when writing has finished")
    return digest, after.st_size


class AssetService:
    def __init__(
        self,
        store: ProjectStore,
        *,
        roots: dict[str, Path] | None = None,
        ffprobe: str = "ffprobe",
        ffmpeg: str = "ffmpeg",
    ):
        if not isinstance(store.read(), Project):
            raise AssetError("project.json must be a project index")
        self.store = store
        self.roots = dict(roots or {})
        if "project" in self.roots:
            raise AssetError("project root cannot be overridden")
        try:
            portable = PortableRoots.model_validate_json(store._read_bytes(".portable-roots.json"))
        except FileNotFoundError:
            pass
        else:
            for identity in portable.roots:
                with store._directory((".portable-media", identity)):
                    self.roots[identity] = store.root / ".portable-media" / identity
        self.ffprobe, self.ffmpeg = ffprobe, ffmpeg

    def resolve(self, location: MediaPath) -> Path:
        return resolve_media_path(location, self.store.root, self.roots)

    def load(self, reference: AssetRef) -> Asset:
        reference = AssetRef.model_validate(reference)
        asset = self.store.read(f"registry/assets/{reference.id}/{reference.version}.json")
        if not isinstance(asset, Asset) or (asset.id, asset.version) != (
            reference.id,
            reference.version,
        ):
            raise AssetError("registry document does not match its requested identity")
        return asset

    def list_assets(self) -> list[Asset]:
        folder = self.store.root / "registry" / "assets"
        return [
            self.load(AssetRef(id=path.parent.name, version=path.stem))
            for path in sorted(folder.glob("*/*.json"))
        ]

    def _record(self, location: MediaPath) -> HashedFile:
        digest, size = digest_file(self.resolve(location))
        return HashedFile(location=location, sha256=digest, size_bytes=size)

    def _health(self, record: HashedFile) -> FileHealth:
        observed, message = None, None
        try:
            observed, size = digest_file(self.resolve(record.location))
            status = "ok" if (observed, size) == (record.sha256, record.size_bytes) else "changed"
        except FileNotFoundError as error:
            status, message = "missing", str(error)
        except (OSError, StorageError) as error:
            status, message = "inaccessible", str(error)
        return FileHealth(
            location=record.location,
            expected_sha256=record.sha256,
            observed_sha256=observed,
            status=status,
            message=message,
        )

    def check(self, reference: AssetRef) -> AssetHealth:
        asset = self.load(reference)
        files = [self._health(record) for record in asset.files]
        proxies = [self._health(record) for record in asset.proxies]
        valid = all(record.status == "ok" for record in files)
        approved = valid and asset.approval.status == "approved"
        try:
            source_available = self.resolve(asset.source).is_file()
        except (OSError, StorageError):
            source_available = False
        return AssetHealth(
            schema_version="1.0",
            asset=reference,
            content_sha256=asset.approval_hash,
            files=files,
            proxies=proxies,
            source_available=source_available,
            media_valid=valid,
            approval_valid=approved,
            rights=asset.provenance.commercial_use,
            publication_ready=approved
            and asset.provenance.commercial_use == "confirmed"
            and asset.provenance.origin != "synthetic",
        )

    def require_valid(self, reference: AssetRef, *, production: bool = False) -> Asset:
        health = self.check(reference)
        if not health.media_valid or (production and not health.publication_ready):
            raise AssetError(
                f"asset {reference.id}@{reference.version} "
                "is missing, changed or not approved for this use"
            )
        asset = self.load(reference)
        if asset.approval_hash != health.content_sha256 or (
            production and asset.approval.status != "approved"
        ):
            raise AssetError("registry changed during validation; retry with the new version")
        return asset

    def _commit_media(self, staging: Path, folder: str, asset: Asset) -> Asset:
        """Publish validated media first and registry last, under the writer lock.

        A process crash can leave an unreferenced, uniquely named media folder;
        it cannot publish a registry pointing at a half-copied source. No source
        directory is ever a cleanup target.
        """
        relative = document_path(asset)
        with self.store.writer_lock():
            try:
                self.store._read_bytes(relative)
            except FileNotFoundError:
                pass
            else:
                raise AssetError("asset version exists; choose a new immutable version")
            parts = self.store._parts(folder)
            with self.store._directory(parts[:-1], create=True) as parent:
                os.mkdir(parts[-1], mode=0o700, dir_fd=parent)
                target = self.store.root / folder
                try:
                    os.replace(staging, target)
                    os.fsync(parent)
                    self.store._atomic_write(relative, canonical_bytes(asset), overwrite=False)
                except BaseException:
                    # Only this invocation's new UUID directory is removable.
                    # Preserve it if publication reached disk before a flush failure.
                    try:
                        self.store._read_bytes(relative)
                    except FileNotFoundError:
                        shutil.rmtree(target)
                    raise
        return asset

    def import_asset(self, request: ImportRequest) -> Asset:
        request = ImportRequest.model_validate(request)
        if len({(path.root_id, path.path) for path in request.paths}) != len(request.paths):
            raise AssetError("duplicate input files")
        paths = [self.resolve(path) for path in request.paths]
        for path in paths:
            if not path.is_file():
                raise AssetError(f"source is missing or is not a regular file: {path}")
        before = [self._record(path) for path in request.paths]
        probe = probe_media(
            paths, request.kind, fps=request.fps, ffprobe=self.ffprobe, ffmpeg=self.ffmpeg
        )
        if before != [self._record(path) for path in request.paths]:
            raise AssetError("source changed during probing")
        common = dict(
            schema_version="1.0",
            document_type="asset",
            id=request.id,
            version=request.version,
            kind=request.kind,
            source=request.paths[0],
            probe=probe,
            compatibility=request.compatibility,
            provenance=request.provenance,
        )
        if request.mode == "link":
            asset = Asset(**common, files=before)
            self.store.save_draft(asset, expected_revision=None)
            return asset
        folder = f"sources/{request.id}/{request.version}-{uuid4().hex}"
        with tempfile.TemporaryDirectory(prefix=".tabi-import-", dir=self.store.root) as scratch:
            stage = Path(scratch) / "media"
            stage.mkdir()
            records = []
            for index, (path, original) in enumerate(zip(paths, before, strict=True)):
                name = f"{index:06d}-{path.name}"
                output = stage / name
                with path.open("rb") as source, output.open("xb") as destination:
                    shutil.copyfileobj(source, destination, length=1024 * 1024)
                    destination.flush()
                    os.fsync(destination.fileno())
                if digest_file(output) != (original.sha256, original.size_bytes):
                    raise AssetError("copy verification failed; source may have changed")
                records.append(
                    HashedFile(
                        location=MediaPath(path=f"{folder}/{name}"),
                        sha256=original.sha256,
                        size_bytes=original.size_bytes,
                    )
                )
            asset = Asset(**common, files=records)
            return self._commit_media(stage, folder, asset)

    def relink(self, reference: AssetRef, *, version: str, paths: list[MediaPath]) -> Asset:
        old = self.load(reference)
        if version_tuple(version) <= version_tuple(old.version):
            raise AssetError("relink requires a newer version; old approvals remain immutable")
        if len(paths) != len(old.files):
            raise AssetError("relink must supply every file in the original sequence order")
        records = [self._record(path) for path in paths]
        if [(r.sha256, r.size_bytes) for r in records] != [
            (r.sha256, r.size_bytes) for r in old.files
        ]:
            raise AssetError(
                "relink hashes do not match; import changed content as a new asset version"
            )
        data = old.model_dump(mode="json")
        data.update(
            version=version,
            revision=0,
            approval={"status": "draft"},
            proxies=[],
            source=paths[0].model_dump(mode="json"),
            files=[r.model_dump(mode="json") for r in records],
        )
        result = validate_data(data)
        self.store.save_draft(result, expected_revision=None)
        return result

    def approve(
        self, reference: AssetRef, *, expected_hash: str, reviewer: str, note: str
    ) -> Asset:
        """Explicit human review command; tests and imports never call this automatically."""
        asset = self.require_valid(reference)
        if asset.approval_hash != expected_hash:
            raise AssetError("reviewed hash is stale; inspect the current content before approval")
        if asset.provenance.origin in {"unknown", "synthetic"}:
            raise AssetError(
                "unknown provenance or synthetic fixtures cannot be production approved"
            )
        if asset.provenance.commercial_use != "confirmed":
            raise AssetError(
                "rights are pending or not permitted; record evidence in a new version"
            )
        approval = Approval(
            status="approved",
            content_sha256=expected_hash,
            reviewer=reviewer,
            reviewed_at=datetime.now(UTC),
            note=note,
        )
        data = asset.model_dump(mode="json")
        data["approval"] = approval.model_dump(mode="json")
        result = validate_data(data)
        return self.store.save_draft(result, expected_revision=asset.revision)

    def image_proxies(self, reference: AssetRef, *, version: str, max_edge: int = 640) -> Asset:
        """Make color-managed PNG thumbnails, retaining the original working files.

        Proxy hashes live in a new draft version. They are disposable previews,
        not normalized production masters. Untagged RGB is explicitly interpreted
        as sRGB for the preview only; mask coverage is never color transformed.
        """
        if type(max_edge) is not int or not 16 <= max_edge <= 4096:
            raise AssetError("proxy edge must be between 16 and 4096 pixels")
        old = self.require_valid(reference)
        if old.kind not in {"still", "sequence", "mask"}:
            raise AssetError("PNG proxy preparation accepts stills, masks and image sequences")
        if version_tuple(version) <= version_tuple(old.version):
            raise AssetError("proxy records require a newer draft version")
        folder = f"assets/{old.id}/proxies-{version}-{uuid4().hex}"
        with tempfile.TemporaryDirectory(prefix=".tabi-proxy-", dir=self.store.root) as scratch:
            stage = Path(scratch) / "media"
            stage.mkdir()
            records = []
            for index, record in enumerate(old.files):
                with Image.open(self.resolve(record.location)) as source:
                    source.load()
                    image = ImageOps.exif_transpose(source)
                    if old.kind == "mask":
                        image = image.convert("L")
                    elif profile := source.info.get("icc_profile"):
                        image = ImageCms.profileToProfile(
                            image,
                            ImageCms.ImageCmsProfile(io.BytesIO(profile)),
                            ImageCms.createProfile("sRGB"),
                            outputMode="RGBA",
                        )
                    else:
                        image = image.convert("RGBA")
                    image.thumbnail((max_edge, max_edge), Image.Resampling.LANCZOS)
                    name = f"{index:06d}.png"
                    output = stage / name
                    image.save(output, format="PNG")
                image_probe(output, mask=old.kind == "mask")
                digest, size = digest_file(output)
                records.append(
                    HashedFile(
                        location=MediaPath(path=f"{folder}/{name}"), sha256=digest, size_bytes=size
                    )
                )
            # Catch source mutation between the initial check and proxy generation.
            self.require_valid(reference)
            data = old.model_dump(mode="json")
            data.update(
                version=version,
                revision=0,
                approval={"status": "draft"},
                proxies=[r.model_dump(mode="json") for r in records],
            )
            return self._commit_media(stage, folder, validate_data(data))
