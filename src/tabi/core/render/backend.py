"""Renderer interface and verified access to a frozen registry snapshot."""

import hashlib
from pathlib import Path
from typing import Protocol

from ..assets import AssetService
from ..models import Asset, CompiledSnapshot
from ..models.base import AssetRef, Canvas, content_hash
from ..models.production import Fingerprint, OutputProfile
from ..models.rendering import RenderReport


class RenderError(ValueError):
    pass


def backend_fingerprint() -> Fingerprint:
    digest = hashlib.sha256()
    for path in sorted(Path(__file__).parent.glob("*.py")):
        digest.update(path.name.encode() + b"\0" + path.read_bytes())
    return Fingerprint(name="tabi-ffmpeg", version="1", sha256=digest.hexdigest())


class Renderer(Protocol):
    def frame(
        self, snapshot: CompiledSnapshot, frame: int, output: Path, *, canvas: Canvas | None = None
    ) -> RenderReport: ...

    def clip(
        self, snapshot: CompiledSnapshot, start: int, end: int, output: Path, profile: OutputProfile
    ) -> RenderReport: ...


class FrozenRegistry:
    def __init__(
        self, assets: AssetService, snapshot: CompiledSnapshot, *, require_approval: bool = True
    ):
        self.assets = assets
        self.snapshot = CompiledSnapshot.model_validate(snapshot)
        if (
            require_approval
            and snapshot.purpose == "production"
            and snapshot.approval.status != "approved"
        ):
            raise RenderError("production rendering requires review of this frozen snapshot hash")
        self.documents = {}
        self.verify()

    def verify(self) -> None:
        documents = {}
        for lock in self.snapshot.locked_assets:
            found = []
            for folder in ("assets", "templates", "actions"):
                try:
                    found.append(
                        self.assets.store.read(f"registry/{folder}/{lock.id}/{lock.version}.json")
                    )
                except FileNotFoundError:
                    pass
            if len(found) != 1 or content_hash(found[0]) != lock.sha256:
                raise RenderError(
                    f"frozen registry lock changed or missing: {lock.id}@{lock.version}"
                )
            document = found[0]
            if isinstance(document, Asset):
                self.assets.require_valid(
                    AssetRef(id=lock.id, version=lock.version),
                    production=self.snapshot.purpose == "production",
                )
            elif self.snapshot.purpose == "production" and document.approval.status != "approved":
                raise RenderError("production template/pack approval is missing")
            documents[(lock.id, lock.version)] = document
        self.documents = documents

    def get(self, ref: AssetRef, kind: str):
        document = self.documents.get((ref.id, ref.version))
        if document is None or document.document_type != kind:
            raise RenderError(f"snapshot lacks a locked {kind}: {ref.id}@{ref.version}")
        return document
