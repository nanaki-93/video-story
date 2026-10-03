import pytest

from tabi.core.config import load_settings
from tabi.core.persistence import RevisionConflict
from tabi.core.preferences import PreferencesService


def test_settings_use_revision_hash_guards_and_back_up_exact_config(tmp_path):
    settings = load_settings(None, env={}, cwd=tmp_path, home=tmp_path)
    service = PreferencesService(settings)
    defaults, saved = service.read()
    assert not saved and defaults.cache_budget_bytes == 20 * 1024**3
    prefs = service.save(defaults.model_copy(update={"theme": "contrast"}), None)
    assert service.read() == (prefs, True)
    with pytest.raises(RevisionConflict):
        service.save(defaults, None)
    updated = service.save(prefs.model_copy(update={"cache_budget_bytes": 0}), prefs.revision)
    assert updated.revision == prefs.revision + 1
    with pytest.raises(RevisionConflict):
        service.save(prefs, prefs.revision)
    digest = service.save_tools('/工具/ffmpeg with "quotes"', "ffprobe", None)
    original = settings.config_file.read_bytes()
    configured = load_settings(settings.config_file, env={}, cwd=tmp_path, home=tmp_path)
    assert configured.ffmpeg == '/工具/ffmpeg with "quotes"'
    with pytest.raises(RevisionConflict):
        service.save_tools("wrong", "wrong", None)
    assert settings.config_file.read_bytes() == original
    assert service.save_tools("new-ffmpeg", "new-ffprobe", digest) != digest
    backups = [p for p in (settings.config_file.parent / ".backups").rglob("*") if p.is_file()]
    assert any(p.read_bytes() == original for p in backups)
