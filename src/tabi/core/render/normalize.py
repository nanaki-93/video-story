"""Owned, verified PNG interchange copies. Original media is never modified."""

import io
from pathlib import Path

from PIL import Image, ImageCms

from ..cache.keys import image_descriptor
from ..cache.store import CacheStore
from ..models import Asset
from ..models.base import content_hash
from ..process import checkpoint
from .backend import FrozenRegistry, RenderError


class ImageNormalizer:
    def __init__(self, registry: FrozenRegistry, folder: Path):
        self.registry = registry
        self.folder = folder
        folder.mkdir()
        self.prepared: dict[str, Path] = {}
        self.warnings: set[str] = set()
        self.cache = CacheStore(registry.assets.store)
        self.cache_hits = 0

    def prepare(self, asset: Asset, frame: int = 0) -> Path:
        checkpoint()
        if asset.kind not in {"still", "mask", "sequence"}:
            raise RenderError(
                "this backend needs prepared PNG stills/sequences; "
                "export video to reviewed RGBA frames"
            )
        if asset.probe.pixel_aspect.num != asset.probe.pixel_aspect.den:
            raise RenderError("non-square source pixels need explicit preparation")
        if frame < 0 or frame >= len(asset.files):
            raise RenderError("source frame is outside its prepared media")
        record = asset.files[frame]
        descriptor = image_descriptor(asset, frame, self.registry.snapshot.purpose)
        key = content_hash(descriptor)
        if key in self.prepared:
            return self.prepared[key]
        output = self.folder / f"{key}.png"
        cached = self.cache.lookup("normalized_image", descriptor, destination=output)
        if cached:
            try:
                with Image.open(output) as verified:
                    verified.load()
                    canvas = asset.compatibility.crop or asset.probe.canvas
                    if verified.mode != ("L" if asset.kind == "mask" else "RGBA") or (
                        verified.size != (canvas.width, canvas.height)
                    ):
                        raise RenderError("cached PNG has incompatible dimensions or mode")
                self.warnings.update(cached.warnings)
                self.prepared[key] = output
                self.cache_hits += 1
                return output
            except (ValueError, OSError):
                output.unlink()  # New scratch link only; preserve the cache/source bytes.
        warnings = set()
        path = self.registry.assets.resolve(record.location)
        with Image.open(path) as source:
            source.load()
            if source.size != (asset.probe.canvas.width, asset.probe.canvas.height):
                raise RenderError("source image dimensions differ from frozen probe metadata")
            if source.getexif().get(274, 1) != 1:
                raise RenderError("source requires explicit orientation preparation")
            if asset.kind == "mask":
                if source.mode not in {"1", "L"} or source.info.get("icc_profile"):
                    raise RenderError("mask requires untagged grayscale coverage")
                image = source.convert("L")
            else:
                if asset.probe.alpha_mode not in {"straight", "premultiplied", "none"}:
                    raise RenderError("source alpha convention is unknown")
                image = source.convert("RGBA")
                if asset.probe.alpha_mode == "premultiplied":
                    image = Image.frombytes("RGBa", image.size, image.tobytes()).convert("RGBA")
                if profile := source.info.get("icc_profile"):
                    image = ImageCms.profileToProfile(
                        image,
                        ImageCms.ImageCmsProfile(io.BytesIO(profile)),
                        ImageCms.createProfile("sRGB"),
                        outputMode="RGBA",
                    )
                elif asset.probe.color_space not in {"srgb", "grayscale"}:
                    if self.registry.snapshot.purpose == "production":
                        raise RenderError(
                            "untagged source color needs explicit sRGB preparation/approval"
                        )
                    warnings.add(f"{asset.id}: untagged RGB interpreted as sRGB for draft preview")
            if crop := asset.compatibility.crop:
                image = image.crop((crop.x, crop.y, crop.x + crop.width, crop.y + crop.height))
            # Numeric mask values and straight-alpha edge colors stay unchanged.
            image.info.clear()
            image.save(output, format="PNG")
            with Image.open(output) as verified:
                verified.load()
                if (
                    verified.mode != image.mode
                    or verified.size != image.size
                    or verified.tobytes() != image.tobytes()
                ):
                    raise RenderError("normalized PNG failed independent decode verification")
        self.warnings.update(warnings)
        self.cache.put(
            "normalized_image", descriptor, output, warnings=warnings, refresh=bool(cached)
        )
        self.prepared[key] = output
        return output
