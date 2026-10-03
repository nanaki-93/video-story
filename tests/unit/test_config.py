from pathlib import Path

import pytest

from tabi.core.config import ConfigError, load_settings


def resolve(tmp_path: Path, config: Path | None = None, **env: str):
    return load_settings(config, env=env, cwd=tmp_path, home=tmp_path / "home")


def test_defaults_do_not_create_project_or_cache(tmp_path):
    settings = resolve(tmp_path)
    assert not settings.config_loaded
    assert not settings.project_root.exists()
    assert not settings.cache_root.exists()
    assert settings.ffmpeg == "ffmpeg"


def test_config_and_environment_precedence_and_unicode(tmp_path):
    folder = tmp_path / "東京 settings"
    folder.mkdir()
    config = folder / "config.toml"
    config.write_text(
        'schema_version = "1.0"\n[paths]\nproject_root = "../My projects"\n'
        'cache_root = "cache"\n[tools]\nffmpeg = "tools/ffmpeg"\n',
        encoding="utf-8",
    )
    settings = resolve(tmp_path, config, TABI_CACHE_ROOT="local cache", TABI_CONFIG="missing.toml")
    assert settings.project_root == tmp_path / "My projects"
    assert settings.cache_root == tmp_path / "local cache"
    assert settings.ffmpeg == str(folder / "tools/ffmpeg")
    assert settings.config_loaded


def test_default_config_can_be_selected_with_xdg(tmp_path):
    config = tmp_path / "prefs" / "tabi" / "config.toml"
    config.parent.mkdir(parents=True)
    config.write_text('schema_version = "1.0"\n[paths]\nproject_root = "~/Episodes"\n')
    settings = resolve(tmp_path, XDG_CONFIG_HOME="prefs")
    assert settings.config_file == config
    assert settings.project_root == tmp_path / "home" / "Episodes"


@pytest.mark.parametrize(
    "content",
    [
        'schema_version = "2.0"',
        'schema_version = "1.1"',
        'schema_version = "1.0"\nunknown = true',
        'schema_version = "1.0"\n[tools]\nffmepg = "ffmpeg"',
        'schema_version = "1.0"\n[paths]\ncache_root = 12',
        'schema_version = "1.0"\n[tools]\nffmpeg = ""',
        'schema_version = "1.0"\npaths = []',
        "schema_version = [",
        "",
    ],
)
def test_invalid_settings_fail_without_writes(tmp_path, content):
    config = tmp_path / "config.toml"
    config.write_text(content)
    with pytest.raises(ConfigError):
        resolve(tmp_path, config)
    assert config.read_text() == content


def test_missing_explicit_file_is_not_silently_ignored(tmp_path):
    with pytest.raises(ConfigError, match="does not exist"):
        resolve(tmp_path, TABI_CONFIG="missing.toml")


def test_empty_environment_override_is_rejected(tmp_path):
    with pytest.raises(ConfigError, match="TABI_FFMPEG"):
        resolve(tmp_path, TABI_FFMPEG="")
