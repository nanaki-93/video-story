import json
from pathlib import Path

import pytest

from tabi.cli.main import main
from tabi.core.audio.pcm import PCMReader
from tabi.core.fixtures import generate_fixtures
from tabi.core.persistence import ProjectStore


@pytest.mark.media
def test_cli_audio_audition_then_compile_queue_progress_and_verified_export(tmp_path, capsys):
    project = tmp_path / "CLI render 東京"
    generate_fixtures(project)
    store = ProjectStore(project)
    episode = store.read("episodes/episode.synthetic.json")
    request = tmp_path / "audio.json"
    request.write_text(
        json.dumps(
            {
                "expected_revision": 0,
                "tracks": [
                    {
                        **episode.tracks[0].model_dump(mode="json"),
                        "trim_end_sample": 48000,
                        "gain_db": -6.0,
                    }
                ],
            }
        )
    )

    def cli(*args):
        assert main(list(map(str, args))) == 0
        return json.loads(capsys.readouterr().out)

    saved = cli("audio", "edit", episode.id, request, "--project", project)
    audition = cli(
        "audio",
        "audition",
        episode.id,
        "--expected-revision",
        saved["revision"],
        "--end-sample",
        48000,
        "--project",
        project,
    )
    with PCMReader(Path(audition["path"])) as source:
        assert source.samples == 48000 and source.rate == 48000
        assert source.channels == 2 and source.read(1000, 1000).any()
    compiled = cli(
        "compile",
        project / "episodes/episode.synthetic.json",
        "--purpose",
        "synthetic_test",
        "--project",
        project,
    )
    job = cli(
        "jobs",
        "submit",
        compiled["snapshot_sha256"],
        "--project",
        project,
        "--output",
        "exports/cli.mp4",
        "--end",
        30,
        "--width",
        320,
        "--height",
        180,
        "--chunk-frames",
        13,
    )
    before = cli("jobs", "progress", job["id"], "--project", project)
    assert before["job"]["state"] == "queued" and before["eta_seconds"] is None
    assert cli("jobs", "work", "--once", "--project", project)[0]["state"] == "verified"
    after = cli("jobs", "progress", job["id"], "--project", project)
    assert after["job"]["completed_frames"] == 30 and after["elapsed_running_seconds"] > 0
    verified = cli("jobs", "verify", job["id"], "--project", project)
    assert verified["video"]["frame_count"] == 30 and verified["audio"]["decoded_samples"] == 48000
