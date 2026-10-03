"""Standard-library build checks shared by the release script and isolated Hatch builds."""

import hashlib
import json
import tomllib
from pathlib import Path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inputs(root):
    paths = [
        *root.joinpath("web/src").rglob("*"),
        *root.joinpath("web/scripts").rglob("*"),
        *root.joinpath("schemas").glob("*.json"),
        *(
            root / name
            for name in (
                "web/package.json",
                "web/package-lock.json",
                "web/index.html",
                "web/vite.config.ts",
                "web/tsconfig.json",
            )
        ),
    ]
    return {p.relative_to(root).as_posix(): digest(p) for p in sorted(paths) if p.is_file()}


def stamp_frontend(root):
    root = Path(root)
    output = root / "web/dist"
    assets = output / "assets"
    notices = ["Third-party code used by the built Tabi browser client.\n"]
    for name in (
        "ajv",
        "ajv-formats",
        "fast-uri",
        "fast-deep-equal",
        "json-schema-traverse",
        "require-from-string",
    ):
        package = root / "web/node_modules" / name
        meta = json.loads((package / "package.json").read_text())
        licence = next(p for p in package.iterdir() if p.name.lower() == "license")
        notices.append(f"\n{name} {meta['version']} — {meta['license']}\n\n{licence.read_text()}")
    (assets / "THIRD-PARTY-NOTICES.txt").write_text("\n".join(notices), encoding="utf-8")
    project = tomllib.loads((root / "pyproject.toml").read_text())["project"]
    record = {
        "format": 1,
        "version": project["version"],
        "protocol": "1",
        "inputs": inputs(root),
        "files": {
            p.relative_to(output).as_posix(): digest(p)
            for p in sorted(output.rglob("*"))
            if p.is_file() and p.name != "build-info.json"
        },
    }
    (assets / "build-info.json").write_text(json.dumps(record, sort_keys=True, indent=2) + "\n")
    return record


def verify_frontend(root):
    root = Path(root)
    output = root / "web/dist"
    try:
        record = json.loads((output / "assets/build-info.json").read_text())
    except (FileNotFoundError, ValueError) as error:
        raise ValueError(
            "Packaged frontend missing. Run make package (requires build-time Node/npm)."
        ) from error
    version = tomllib.loads((root / "pyproject.toml").read_text())["project"]["version"]
    if record["inputs"] != inputs(root) or record["version"] != version:
        raise ValueError("Frontend sources changed since the build; run make package again")
    actual = {
        p.relative_to(output).as_posix(): digest(p)
        for p in sorted(output.rglob("*"))
        if p.is_file() and p.name != "build-info.json"
    }
    if (
        record["files"] != actual
        or "index.html" not in actual
        or not any(p.endswith(".js") for p in actual)
    ):
        raise ValueError("Built frontend inventory/hash mismatch; run make package again")
    if any(
        Path(name).suffix.lower() in {".mp4", ".ttf", ".otf", ".dylib", ".so"} for name in actual
    ):
        raise ValueError(
            "Media, commercial fonts and runtime binaries must not enter this distribution"
        )
    return record
