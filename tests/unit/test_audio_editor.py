import pytest

from tabi.core.assets import AssetService
from tabi.core.audio.editor import AudioEdit, AudioEditor
from tabi.core.config import load_settings
from tabi.core.fixtures import generate_fixtures
from tabi.core.persistence import ProjectStore, RevisionConflict


def test_audio_resequence_keeps_visuals_and_rejects_duration_conflicts(tmp_path):
    root = tmp_path / "audio"
    generate_fixtures(root)
    settings = load_settings(None, env={}, cwd=tmp_path, home=tmp_path)
    editor = AudioEditor(AssetService(ProjectStore(root)), settings)
    original = editor.author.episode("episode.synthetic")
    first = {**original.tracks[0].model_dump(), "id": "first", "trim_end_sample": 120000}
    second = {**first, "id": "second", "gain_db": -6.0}
    edit = AudioEdit(expected_revision=0, tracks=[second, first], resequence_music=True)
    proposal, _ = editor.propose(original.id, edit)
    assert proposal.can_apply and proposal.effective_end_sample == 240000
    assert [t.start_sample for t in proposal.tracks] == [0, 120000]
    saved = editor.apply(original.id, edit)
    assert saved.scenes == original.scenes and saved.actions == original.actions
    with pytest.raises(RevisionConflict):
        editor.apply(original.id, edit)
    before = editor.store._read_bytes("episodes/episode.synthetic.json")
    invalid = AudioEdit(expected_revision=1, tracks=[{**first, "start_sample": 480000}])
    plan, _ = editor.propose(original.id, invalid)
    assert not plan.can_apply and "beyond story end" in plan.issues[0]
    with pytest.raises(ValueError):
        editor.apply(original.id, invalid)
    assert editor.store._read_bytes("episodes/episode.synthetic.json") == before
    wrong_trim = AudioEdit(expected_revision=1, tracks=[{**first, "trim_end_sample": 480001}])
    assert not editor.propose(original.id, wrong_trim)[0].can_apply
