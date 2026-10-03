"""Atomic local settings, with stale-write checks and configuration backups."""

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from .config import load_settings
from .models.settings import AppPreferences
from .persistence import ProjectStore, RevisionConflict


class PreferencesService:
    def __init__(self, settings):
        self.settings = settings
        root = settings.cache_root / "launcher"
        root.mkdir(parents=True, exist_ok=True)
        self.store = ProjectStore(root)

    def read(self):
        try:
            return self.store.read("preferences/local.json"), True
        except FileNotFoundError:
            return AppPreferences(schema_version="1.0"), False

    def save(self, value, expected_revision):
        return self.store.save_draft(
            AppPreferences.model_validate(value), expected_revision=expected_revision
        )

    def config_hash(self):
        path = self.settings.config_file
        try:
            return hashlib.sha256(ProjectStore(path.parent)._read_bytes(path.name)).hexdigest()
        except FileNotFoundError:
            return None

    def save_tools(self, ffmpeg, ffprobe, expected_hash):
        path = self.settings.config_file
        path.parent.mkdir(parents=True, exist_ok=True)
        store = ProjectStore(path.parent)
        with store.writer_lock():
            if self.config_hash() != expected_hash:
                raise RevisionConflict("Tool settings changed; reload before saving")
            # Validate existing configuration before replacing it. Keep an exact backup.
            if expected_hash is not None:
                load_settings(path, env={}, cwd=path.parent, home=Path.home())
                store._backup(
                    path.name,
                    store._read_bytes(path.name),
                    datetime.now(UTC).strftime("tools-%Y%m%d%H%M%S%f"),
                )
            values = self.settings
            body = "\n".join(
                [
                    'schema_version = "1.0"',
                    "[paths]",
                    f"project_root = {json.dumps(str(values.project_root), ensure_ascii=False)}",
                    f"cache_root = {json.dumps(str(values.cache_root), ensure_ascii=False)}",
                    "[tools]",
                    f"ffmpeg = {json.dumps(ffmpeg, ensure_ascii=False)}",
                    f"ffprobe = {json.dumps(ffprobe, ensure_ascii=False)}",
                    "",
                ]
            )
            store._atomic_write(path.name, body.encode(), overwrite=expected_hash is not None)
        return self.config_hash()
