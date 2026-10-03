import json

import pytest
from PIL import Image

from tabi.cli.main import main
from tabi.core.fixtures import generate_fixtures

pytestmark = pytest.mark.media


def test_cli_freeze_frame_and_actual_range_preview(tmp_path, capsys):
    project = tmp_path / "CLI's 東京 project"
    generate_fixtures(project)
    assert (
        main(
            [
                "compile",
                str(project / "episodes/episode.synthetic.json"),
                "--project",
                str(project),
                "--purpose",
                "synthetic_test",
            ]
        )
        == 0
    )
    result = json.loads(capsys.readouterr().out)
    digest = result["snapshot_sha256"]
    frame = tmp_path / "frame.png"
    assert (
        main(["frame", digest, "--project", str(project), "--frame", "151", "--output", str(frame)])
        == 0
    )
    report = json.loads(capsys.readouterr().out)
    assert report["snapshot_sha256"] == digest and report["first_frame"] == 151
    with Image.open(frame) as image:
        assert image.size == (640, 360)
    movie = tmp_path / "Range's 東京.mp4"
    assert (
        main(
            [
                "preview",
                digest,
                "--project",
                str(project),
                "--start",
                "149",
                "--end",
                "155",
                "--width",
                "640",
                "--height",
                "360",
                "--output",
                str(movie),
            ]
        )
        == 0
    )
    report = json.loads(capsys.readouterr().out)
    assert report["frame_count"] == 6 and report["first_frame"] == 149
    assert report["full_decode_passed"] and report["timestamps_verified"]
    assert report["snapshot_sha256"] == digest
