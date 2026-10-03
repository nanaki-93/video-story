"""Build the local Python app with verified static UI; no bundled Python/FFmpeg/Node."""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from package_support import stamp_frontend, verify_frontend


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=Path(".local/packages"))
    parser.add_argument("--uv", default="uv")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if not shutil.which("npm"):
        parser.error("Building requires Node/npm. Installing the resulting wheel does not.")
    subprocess.run([sys.executable, "scripts/export_schemas.py", "--check"], cwd=root, check=True)
    subprocess.run(
        ["npm", "ci", "--ignore-scripts", "--no-audit", "--no-fund"], cwd=root / "web", check=True
    )
    subprocess.run(["npm", "run", "build"], cwd=root / "web", check=True)
    stamp_frontend(root)
    verify_frontend(root)
    subprocess.run([args.uv, "build", "--out-dir", str(args.out_dir)], cwd=root, check=True)
    subprocess.run(
        [
            args.uv,
            "export",
            "--frozen",
            "--no-dev",
            "--no-emit-project",
            "--format",
            "requirements-txt",
            "--output-file",
            str(args.out_dir / "requirements.txt"),
        ],
        cwd=root,
        check=True,
        stdout=subprocess.DEVNULL,
    )
    print(f"Built local app and locked runtime requirements in {args.out_dir}")


if __name__ == "__main__":
    main()
