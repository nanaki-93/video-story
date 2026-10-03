"""Strict, side-effect-free resolution of local developer settings.

These settings are not project/episode documents. Their contracts and safe
persistence belong to T03.
"""

import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path


class ConfigError(ValueError):
    """An explicit config file or setting cannot be used."""


@dataclass(frozen=True)
class Settings:
    config_file: Path
    config_loaded: bool
    project_root: Path
    cache_root: Path
    ffmpeg: str
    ffprobe: str

    def as_dict(self) -> dict[str, str | bool]:
        return {
            "config_file": str(self.config_file),
            "config_loaded": self.config_loaded,
            "project_root": str(self.project_root),
            "cache_root": str(self.cache_root),
            "ffmpeg": self.ffmpeg,
            "ffprobe": self.ffprobe,
        }


def _text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        raise ConfigError(f"{name} must be a nonempty string without NUL characters")
    return value


def _path(value: str, base: Path, home: Path) -> Path:
    if value == "~":
        return home
    if value.startswith("~/"):
        return (home / value[2:]).resolve()
    path = Path(value)
    return (path if path.is_absolute() else base / path).resolve()


def load_settings(
    config: Path | None,
    *,
    env: Mapping[str, str],
    cwd: Path,
    home: Path,
) -> Settings:
    """Resolve defaults < TOML < environment; CLI selects the config file.

    File-relative paths resolve beside the TOML file. Environment/CLI-relative
    paths resolve against cwd. Bare tool names remain names for later PATH lookup.
    No directories are created and no media tools are executed.
    """
    home, cwd = home.resolve(), cwd.resolve()
    config_home = _path(
        _text(env.get("XDG_CONFIG_HOME", "~/.config"), "XDG_CONFIG_HOME"), cwd, home
    )
    explicit = config is not None or "TABI_CONFIG" in env
    requested = str(config) if config is not None else env.get("TABI_CONFIG")
    config_file = (
        _path(_text(requested, "config path"), cwd, home)
        if requested is not None
        else config_home / "tabi" / "config.toml"
    )
    try:
        with config_file.open("rb") as source:
            document = tomllib.load(source)
        loaded = True
    except FileNotFoundError as error:
        if explicit:
            raise ConfigError(f"Config file does not exist: {config_file}") from error
        document, loaded = {}, False
    except (OSError, ValueError) as error:
        raise ConfigError(f"Cannot read config file {config_file}: {error}") from error

    unknown = document.keys() - {"schema_version", "paths", "tools"}
    if unknown:
        raise ConfigError(f"Unknown config fields: {', '.join(sorted(unknown))}")
    if loaded and document.get("schema_version") != "1.0":
        raise ConfigError('Config schema_version must be "1.0"; migrations are not implemented yet')

    sections: dict[str, dict[str, str]] = {}
    for section, allowed in {
        "paths": {"project_root", "cache_root"},
        "tools": {"ffmpeg", "ffprobe"},
    }.items():
        values = document.get(section, {})
        if not isinstance(values, dict) or values.keys() - allowed:
            raise ConfigError(
                f"{section} must be a table containing only {', '.join(sorted(allowed))}"
            )
        sections[section] = {key: _text(value, f"{section}.{key}") for key, value in values.items()}

    def resolve_value(section: str, key: str, default: str, *, is_path: bool) -> str:
        variable = f"TABI_{key.upper()}"
        if variable in env:
            value, base = _text(env[variable], variable), cwd
        elif key in sections[section]:
            value, base = sections[section][key], config_file.parent
        else:
            value, base = default, cwd
        return str(_path(value, base, home)) if is_path or "/" in value else value

    return Settings(
        config_file=config_file,
        config_loaded=loaded,
        project_root=Path(
            resolve_value("paths", "project_root", "~/Tabi Story Studio/projects", is_path=True)
        ),
        cache_root=Path(resolve_value("paths", "cache_root", "~/.cache/tabi", is_path=True)),
        ffmpeg=resolve_value("tools", "ffmpeg", "ffmpeg", is_path=False),
        ffprobe=resolve_value("tools", "ffprobe", "ffprobe", is_path=False),
    )
