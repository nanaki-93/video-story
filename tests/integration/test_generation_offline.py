import os
import socket
from pathlib import Path

import pytest

from tabi.core.assets import AssetService
from tabi.core.config import load_settings
from tabi.core.fixtures import generate_fixtures
from tabi.core.generation import GenerationService
from tabi.core.jobs import JobService
from tabi.core.models.generation import GenerationPolicy
from tabi.core.persistence import ProjectStore
from tabi.core.preferences import PreferencesService
from tabi.core.render.profiles import preset_profile
from tabi.core.timeline.compiler import ActionCompiler


@pytest.mark.media
def test_real_renderer_is_independent_of_enabled_but_offline_generation(tmp_path):
    root = tmp_path / "Offline generation render"
    generate_fixtures(root, profile="cafe")
    settings = load_settings(
        None,
        env={**os.environ, "TABI_CACHE_ROOT": str(tmp_path / "cache")},
        cwd=Path.cwd(),
        home=tmp_path,
    )
    assets = AssetService(ProjectStore(root))
    # Own the port without listening: no unrelated server can occupy it during this check.
    with socket.socket() as reserved:
        reserved.bind(("127.0.0.1", 0))
        preferences = PreferencesService(settings)
        before, _ = preferences.read()
        preferences.save(
            before.model_copy(
                update={
                    "generation": GenerationPolicy(
                        enabled=True, endpoint=f"http://127.0.0.1:{reserved.getsockname()[1]}"
                    )
                }
            ),
            None,
        )
        assert GenerationService(assets, settings).status(probe=True).availability == "offline"
        episode = assets.store.read("episodes/episode.synthetic.json")
        snapshot = ActionCompiler(assets, purpose="synthetic_test").compile(episode)
        digest = assets.store.save_snapshot(snapshot)
        jobs = JobService(assets, settings)
        job = jobs.submit(
            digest, preset_profile("proxy", fps=episode.fps), "exports/offline.mp4", end_frame=30
        )
        result = jobs.work(once=True)[0]
        assert result.state == "verified", result.error
        verified = jobs.verify_export(job.id)
        assert verified.video.frame_count == 30 and verified.audio.decoded_samples == 48000
