"""Read-only image/hash inventory and contact sheets; not an approval/import service.

Run with the optional audit dependency group. Outputs must live outside the asset
root. Videos receive hashes here; native/FFmpeg decoding is a separate check.
"""

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps


def contact_sheets(paths: list[Path], root: Path, output: Path, prefix: str) -> list[str]:
    output.mkdir(parents=True, exist_ok=True)
    sheets = []
    for first in range(0, len(paths), 30):
        batch = paths[first : first + 30]
        sheet = Image.new("RGB", (1500, 1260), "#efedf0")
        draw = ImageDraw.Draw(sheet)
        draw.text((12, 10), f"{prefix}: supplied assets / technical review only", fill="black")
        for index, path in enumerate(batch):
            x, y = (index % 5) * 300, 40 + (index // 5) * 200
            tile = Image.new("RGBA", (280, 154), "#c4c4cc")
            grid = ImageDraw.Draw(tile)
            for xx in range(0, 280, 14):
                for yy in range(0, 154, 14):
                    if (xx // 14 + yy // 14) % 2:
                        grid.rectangle((xx, yy, xx + 13, yy + 13), fill="#ededf0")
            with Image.open(path) as source:
                thumb = ImageOps.contain(source.convert("RGBA"), tile.size)
                tile.alpha_composite(thumb, ((280 - thumb.width) // 2, (154 - thumb.height) // 2))
            sheet.paste(tile.convert("RGB"), (x + 10, y))
            label = str(path.relative_to(root))
            draw.text((x + 10, y + 158), label[-88:-44], fill="black", font_size=11)
            draw.text((x + 10, y + 174), label[-44:], fill="black", font_size=11)
        destination = output / f"{prefix}-{first // 30 + 1:02d}.jpg"
        sheet.save(destination, quality=90)
        sheets.append(str(destination))
    return sheets


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("docs/assets"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--contact-dir", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    if not root.is_dir():
        parser.error("asset root must be an existing directory")
    for output in (args.output, args.contact_dir):
        if output and output.resolve().is_relative_to(root):
            parser.error("write audit outputs outside the source asset root")
    records = []
    images: dict[str, list[Path]] = defaultdict(list)
    hashes: dict[str, list[str]] = defaultdict(list)
    errors = []
    ignored = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        name = path.relative_to(root).as_posix()
        if path.name == ".DS_Store":
            ignored.append(name)
            continue
        with path.open("rb") as source:
            digest = hashlib.file_digest(source, "sha256").hexdigest()
        record = {
            "path": name,
            "bytes": path.stat().st_size,
            "sha256": digest,
            "extension": path.suffix.lower(),
        }
        hashes[digest].append(name)
        if path.suffix.lower() in {".png", ".jpg", ".jpeg"}:
            try:
                with Image.open(path) as image:
                    image.load()
                    alpha = image.convert("RGBA").getchannel("A")
                    record["image"] = {
                        "width": image.width,
                        "height": image.height,
                        "mode": image.mode,
                        "alpha_range": list(alpha.getextrema()),
                        "alpha_bbox": alpha.getbbox(),
                        "icc_profile_present": bool(image.info.get("icc_profile")),
                    }
                group = path.parent.name if path.stem.startswith("frame-") else "stills"
                images[group].append(path)
            except (OSError, ValueError) as error:
                record["error"] = str(error)
                errors.append(name)
        records.append(record)
    sequences = []
    for group, paths in images.items():
        if group == "stills":
            continue
        indices = [int(path.stem.removeprefix("frame-")) for path in paths]
        sequences.append(
            {
                "path": paths[0].parent.relative_to(root).as_posix(),
                "count": len(indices),
                "first": min(indices),
                "last": max(indices),
                "missing_indices": sorted(
                    set(range(min(indices), max(indices) + 1)) - set(indices)
                ),
                "fps": None,
                "timing_note": (
                    "No authoritative sequence timing metadata supplied; do not infer fps."
                ),
            }
        )
    report = {
        "audit_version": 1,
        "source_root": args.root.as_posix(),
        "approval": "not_assessed",
        "counts": dict(sorted(Counter(record["extension"] for record in records).items())),
        "total_bytes": sum(record["bytes"] for record in records),
        "image_decode_errors": errors,
        "ignored_os_metadata": ignored,
        "duplicate_files": [names for names in hashes.values() if len(names) > 1],
        "sequences": sequences,
        "files": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    sheets = []
    if args.contact_dir:
        for group, paths in images.items():
            sheets.extend(contact_sheets(paths, root, args.contact_dir, group))
    print(
        json.dumps(
            {
                "counts": report["counts"],
                "bytes": report["total_bytes"],
                "errors": errors,
                "sequences": sequences,
                "duplicate_groups": len(report["duplicate_files"]),
                "contact_sheets": sheets,
            },
            ensure_ascii=False,
        )
    )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
