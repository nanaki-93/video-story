import json

import pytest
from fastapi.testclient import TestClient
from PIL import Image
from pydantic import ValidationError

from tabi.api.app import create_app
from tabi.api.runtime import Runtime
from tabi.cli.main import main
from tabi.core.config import load_settings
from tabi.core.documents import DocumentError, validate_data
from tabi.core.fixture_lofi import generate_lofi_fixtures
from tabi.core.lofi import LofiService
from tabi.core.models.base import AssetRef, content_hash
from tabi.core.models.lofi import CreateLofiVideo, LofiScene
from tabi.core.models.scenes import LoopTiming
from tabi.core.persistence import RevisionConflict
from tabi.core.timeline.compiler import ActionCompiler


@pytest.fixture
def scene_project(tmp_path):
    assets, scene = generate_lofi_fixtures(tmp_path / "Reusable 東京")
    service = LofiService(assets)
    return service, service.save(scene, expected_revision=None)


def video(scene, **values):
    return CreateLofiVideo(
        id="video.test",
        title="SYNTHETIC loop video",
        scene=AssetRef(id=scene.id, version=scene.version),
        expected_scene_revision=scene.revision,
        **values,
    )


def test_reusable_recipe_freezes_existing_video_and_rejects_stale_writes(scene_project):
    service, scene = scene_project
    first = service.create_video(video(scene, duration_seconds=3))
    assert first.revision == 0 and first.format == "session" and first.duration_frames == 72
    snapshot = ActionCompiler(service.assets).compile(first)
    digest = content_hash(snapshot)
    updated = LofiScene.model_validate({**scene.model_dump(), "speed": 48.0})
    saved = service.save(updated, expected_revision=0)
    assert saved.revision == 1
    with pytest.raises(RevisionConflict):
        service.save(updated, expected_revision=0)
    with pytest.raises(RevisionConflict, match="scene changed"):
        service.create_video(video(scene))
    assert content_hash(ActionCompiler(service.assets).compile(first)) == digest
    assert service.scenes() == [saved]
    second = service.create_video(video(saved).model_copy(update={"id": "video.second"}))
    assert first.scenes[0].template != second.scenes[0].template


def test_music_fit_preserves_samples_and_failed_requests_create_no_episode(scene_project):
    service, scene = scene_project
    music = [AssetRef(id="lofi.test.music", version="1.0")]
    with pytest.raises(ValueError, match="exceeds video"):
        service.create_video(video(scene, duration_seconds=1, music=music))
    assert not (service.store.root / "episodes/video.test.json").exists()
    episode = service.create_video(video(scene, duration_seconds=None, music=music))
    assert episode.duration_frames == 48
    assert episode.tracks[0].trim_end_sample == 96000
    assert episode.tracks[0].loop_duration_samples is None
    with pytest.raises(ValueError, match="choose music"):
        service.create_video(video(scene, duration_seconds=None))


def test_seconds_input_is_compiled_to_frames_and_unknown_timing_is_rejected(scene_project):
    service, scene = scene_project
    identity = scene.overlays[0].id
    saved = service.save(
        scene,
        expected_revision=0,
        timing_seconds={identity: {"repeat_seconds": 2.25, "delay_seconds": 0.125}},
    )
    assert saved.overlays[0].timing.repeat_frames == 54
    assert saved.overlays[0].timing.first_frame == 3
    assert "seconds" not in saved.model_dump_json()
    with pytest.raises(ValueError, match="unknown overlay"):
        service.save(saved, expected_revision=1, timing_seconds={"typo": {}})
    with pytest.raises(ValidationError, match="truncate"):
        service.save(saved, expected_revision=1, timing_seconds={identity: {"repeat_seconds": 0.1}})
    assert service.scene(AssetRef(id=scene.id, version=scene.version)) == saved


@pytest.mark.parametrize(
    "change",
    [
        {"schema_version": "2.0"},
        {"typo": 1},
        {"window_mask": None},
        {"speed": -1},
        {"fps": {"num": 24.5, "den": 1}},
    ],
)
def test_recipe_rejects_invalid_schema_and_configuration(scene_project, change):
    _, scene = scene_project
    with pytest.raises((ValidationError, DocumentError)):
        validate_data({**scene.model_dump(mode="json"), **change})


def test_overlay_global_timing_gap_and_bounds_are_explicit():
    timing = LoopTiming(source={"start_frame": 3, "end_frame": 6}, repeat_frames=7, first_frame=2)
    assert [timing.source_at(n) for n in range(13)] == [
        None,
        None,
        3,
        4,
        5,
        None,
        None,
        None,
        None,
        3,
        4,
        5,
        None,
    ]
    with pytest.raises(ValidationError, match="truncate"):
        LoopTiming(source={"start_frame": 0, "end_frame": 4}, repeat_frames=3)


def test_bad_strip_overlay_and_changed_assets_fail_before_recipe_save(scene_project):
    service, scene = scene_project
    bad = scene.model_dump(mode="json")
    bad["overlays"][0]["timing"]["source"]["end_frame"] = 5
    with pytest.raises(ValueError, match="overlay needs"):
        service.save(LofiScene.model_validate(bad), expected_revision=0)
    bad = scene.model_dump(mode="json")
    bad["scenery"][0]["repeat_width"] = 127
    with pytest.raises(ValueError, match="opening pixels"):
        service.save(LofiScene.model_validate(bad), expected_revision=0)
    master = service.assets.load(scene.master)
    Image.new("RGB", (320, 180), "white").save(service.assets.resolve(master.files[0].location))
    with pytest.raises(ValueError):
        service.save(scene, expected_revision=0)
    assert service.scene(AssetRef(id=scene.id, version=scene.version)) == scene


def test_api_creates_saved_scene_and_video_with_auth_and_stale_revision(scene_project, tmp_path):
    service, scene = scene_project
    settings = load_settings(None, env={}, cwd=tmp_path, home=tmp_path)
    runtime = Runtime(settings, {"work": service.store.root.parent})
    static = tmp_path / "web"
    static.mkdir()
    (static / "index.html").write_text("Synthetic UI")
    origin = "http://127.0.0.1:54321"
    with TestClient(
        create_app(runtime, origin, static, drive_jobs=False), base_url=origin
    ) as client:
        assert client.get("/api/v1/projects/x/lofi").status_code == 401
        response = client.post(
            "/api/v1/bootstrap",
            json={"protocol": "1", "secret": runtime.sessions.ticket()},
            headers={"Origin": origin},
        )
        headers = {"Origin": origin, "X-Tabi-CSRF": response.json()["csrf"]}
        opened = client.post(
            "/api/v1/projects/open",
            json={"root_id": "work", "path": service.store.root.name},
            headers=headers,
        )
        base = f"/api/v1/projects/{opened.json()['handle']}/lofi"
        assert client.get(base).json()["scenes"][0]["title"] == scene.title
        payload = video(scene, duration_seconds=3).model_dump(mode="json")
        assert client.post(base + "/videos", json=payload).status_code == 403
        created = client.post(base + "/videos", json=payload, headers=headers)
        assert created.status_code == 200, created.text
        assert created.json()["duration_frames"] == 72
        payload["expected_scene_revision"] = 7
        assert client.post(base + "/videos", json=payload, headers=headers).status_code == 409


def test_cli_uses_same_scene_service(scene_project, tmp_path, capsys):
    service, scene = scene_project
    request = tmp_path / "video.json"
    request.write_text(video(scene, duration_seconds=2).model_dump_json())
    assert main(["lofi", "create-video", str(request), "--project", str(service.store.root)]) == 0
    assert json.loads(capsys.readouterr().out)["duration_frames"] == 48
