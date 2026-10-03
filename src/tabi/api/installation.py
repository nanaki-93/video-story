"""Read-only installed app and media dependency check, including bundled static hashes."""

import hashlib
import json
import os
import sys
from pathlib import PurePosixPath

from tabi import __version__
from tabi.core.toolchain import doctor

from .launcher import default_web_root


def setup_check(settings, output_dir):
    problems = []
    if not (3, 11) <= sys.version_info[:2] < (3, 13):
        problems.append(
            "Install Python 3.11 or 3.12 and reinstall the app into a fresh environment."
        )
    if os.name != "posix":
        problems.append(
            "This local launcher requires macOS or a POSIX system; Windows is unsupported."
        )
    frontend = None
    try:
        root = default_web_root()
        record_path = root / "assets/build-info.json"
        frontend = {"path": str(root), "packaged": record_path.is_file(), "verified": False}
        if record_path.is_file():
            record = json.loads(record_path.read_text())
            if record.get("version") != __version__ or record.get("protocol") != "1":
                raise ValueError("Frontend/app version differs; reinstall the matching app wheel.")
            files = record["files"]
            actual = {
                p.relative_to(root).as_posix()
                for p in root.rglob("*")
                if p.is_file() and p != record_path
            }
            if set(files) != actual or "index.html" not in files:
                raise ValueError("Bundled frontend inventory changed; reinstall the app.")
            for relative, expected in files.items():
                path = PurePosixPath(relative)
                if path.is_absolute() or ".." in path.parts or "\\" in relative:
                    raise ValueError("Invalid bundled frontend path; reinstall the app.")
                if hashlib.sha256((root / relative).read_bytes()).hexdigest() != expected:
                    raise ValueError("Bundled frontend hash changed; reinstall the app.")
            frontend["verified"] = True
        else:
            frontend["development_build"] = True
    except (ValueError, OSError, KeyError) as error:
        problems.append(str(error))
    media = doctor(settings, output_dir)
    return {
        "version": __version__,
        "python": sys.version.split()[0],
        "python_executable": sys.executable,
        "frontend": frontend,
        "required_runtime": ["Python 3.11/3.12", "FFmpeg + ffprobe", "Safari or Chromium"],
        "problems": problems,
        "media": media.model_dump(mode="json"),
        "ready": not problems and media.ready,
    }
