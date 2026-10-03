import os
from pathlib import Path

import pytest

from tabi.core.assets import AssetService
from tabi.core.config import load_settings
from tabi.core.models.assets import Provenance
from tabi.core.models.base import AssetRef, MediaPath
from tabi.core.models.registry import ImportRequest
from tabi.core.persistence import ProjectStore
from tabi.core.process import ToolError, run_tool

pytestmark = pytest.mark.media


def test_actual_video_probe_copy_and_corruption(tmp_path):
    settings = load_settings(None, env=os.environ, cwd=Path.cwd(), home=Path.home())
    source = tmp_path / "Owned Marco's 東京 clip.mp4"
    run_tool(
        [
            settings.ffmpeg,
            "-v",
            "error",
            "-nostdin",
            "-f",
            "lavfi",
            "-i",
            "testsrc2=size=128x72:rate=30000/1001",
            "-frames:v",
            "30",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(source),
        ]
    )
    store = ProjectStore.initialize(tmp_path / "project", "Synthetic media import")
    service = AssetService(
        store, roots={"source": tmp_path}, ffmpeg=settings.ffmpeg, ffprobe=settings.ffprobe
    )
    request = ImportRequest(
        id="video.synthetic",
        version="1.0",
        kind="video",
        paths=[MediaPath(root_id="source", path=source.name)],
        provenance=Provenance(origin="synthetic"),
    )
    asset = service.import_asset(request)
    assert asset.probe.frame_count == 30
    assert asset.probe.fps.num == 30000 and asset.probe.fps.den == 1001
    assert service.resolve(asset.files[0].location).read_bytes() == source.read_bytes()
    assert service.check(AssetRef(id=asset.id, version=asset.version)).media_valid
    source.write_bytes(source.read_bytes()[: len(source.read_bytes()) // 2])
    with pytest.raises((ToolError, ValueError)):
        service.import_asset(request.model_copy(update={"version": "1.1"}))
    assert not (store.root / "registry/assets/video.synthetic/1.1.json").exists()
