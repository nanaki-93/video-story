"""Include a checked static frontend in standard wheels and source distributions."""

import runpy
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    def initialize(self, version, build_data):
        if self.target_name == "wheel" and version == "editable":
            return  # Fresh development setup precedes npm/frontend installation.
        root = Path(self.root)
        runpy.run_path(str(root / "scripts/package_support.py"))["verify_frontend"](root)
        build_data["force_include"][str(root / "web/dist")] = (
            "tabi/web" if self.target_name == "wheel" else "web/dist"
        )
