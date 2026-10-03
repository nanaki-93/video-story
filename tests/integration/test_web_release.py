from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from tabi.api.app import create_app
from tabi.api.runtime import Runtime
from tabi.core.assets import AssetService
from tabi.core.config import load_settings
from tabi.core.fixtures import generate_fixtures
from tabi.core.persistence import ProjectStore
from tabi.core.render.ffmpeg import FFmpegRenderer

pytestmark = pytest.mark.media


def test_real_release_http_bundle_backup_restore_and_identical_frame(tmp_path):
    repo = Path(__file__).resolve().parents[2]
    generate_fixtures(tmp_path / "project")
    settings = load_settings(repo / "examples/settings.macos.toml", env={}, cwd=repo, home=tmp_path)
    runtime = Runtime(settings, {"work": tmp_path})
    with TestClient(
        create_app(runtime, "http://testserver", repo / "web/dist", drive_jobs=False)
    ) as client:
        boot = client.post(
            "/api/v1/bootstrap",
            headers={"Origin": "http://testserver"},
            json={"protocol": "1", "secret": runtime.sessions.ticket()},
        )
        headers = {"Origin": "http://testserver", "X-Tabi-CSRF": boot.json()["csrf"]}
        opened = client.post(
            "/api/v1/projects/open", headers=headers, json={"root_id": "work", "path": "project"}
        ).json()
        base = f"/api/v1/projects/{opened['handle']}"
        compilation = client.post(
            base + "/episodes/episode.synthetic/compile",
            headers=headers,
            json={"expected_revision": 0},
        ).json()
        queued = client.post(
            base + "/renders",
            headers=headers,
            json={
                "snapshot_sha256": compilation["snapshot_sha256"],
                "preset": "proxy",
                "encoder": "libx264",
                "destination": "exports/release-test.mp4",
                "end_frame": 30,
            },
        ).json()
        item = runtime.get(opened["handle"])
        job = item.jobs.work(once=True)[0]
        assert job.state == "verified", job.error
        prep = {
            "schema_version": "1.0",
            "document_type": "release_preparation",
            "id": "release-test",
            "job_id": queued["id"],
            "title": "SYNTHETIC engineering sample",
            "claim_notes": "PRIVATE-NOTES",
            "manual_links": ["https://example.test/test-record-only"],
        }
        saved = client.post(base + "/releases", headers=headers, json={"preparation": prep}).json()
        inspected = client.post(base + "/releases/release-test/inspect", headers=headers, json={})
        assert inspected.status_code == 200, inspected.text
        assert "synthetic_assets" in inspected.json()["blockers"]
        assert "manual_links" not in inspected.json()["public"]
        assert (
            client.post(
                base + "/releases/release-test/export",
                headers=headers,
                json={"bundle_id": "not-ready", "require_ready": True},
            ).status_code
            == 400
        )
        bundle = client.post(
            base + "/releases/release-test/export", headers=headers, json={"bundle_id": "draft"}
        )
        assert bundle.status_code == 200, bundle.text
        for index, file in enumerate(bundle.json()["files"]):
            response = client.get(base + f"/bundles/draft/files/{index}")
            if file["location"]["path"].startswith("bundles/draft/public/"):
                assert response.status_code == 200
                if file["location"]["path"].endswith(".txt"):
                    assert (
                        "PRIVATE-NOTES" not in response.text and "example.test" not in response.text
                    )
            else:
                assert response.status_code == 403
        saved["description"] = "Edited before backup"
        updated = client.post(
            base + "/releases",
            headers=headers,
            json={"preparation": saved, "expected_revision": saved["revision"]},
        )
        assert updated.status_code == 200
        assert (
            client.post(
                base + "/releases",
                headers=headers,
                json={"preparation": saved, "expected_revision": saved["revision"]},
            ).status_code
            == 409
        )
        snapshot = item.assets.store.read_snapshot(job.snapshot_sha256)
        first = FFmpegRenderer(item.assets, settings).frame(snapshot, 150, tmp_path / "before.png")
        backup = client.post(
            base + "/backup",
            headers=headers,
            json={"root_id": "work", "folder": "Private backup 東京"},
        )
        assert backup.status_code == 200, backup.text
        restored = client.post(
            "/api/v1/backups/restore",
            headers=headers,
            json={
                "root_id": "work",
                "folder": "Restored 東京",
                "source_root_id": "work",
                "source_path": "Private backup 東京",
            },
        )
        assert restored.status_code == 200, restored.text
        copy = AssetService(ProjectStore(tmp_path / "Restored 東京"))
        assert copy.store.read("publishing/release-test.json").description == "Edited before backup"
        second = FFmpegRenderer(copy, settings).frame(snapshot, 150, tmp_path / "after.png")
        assert first.output_sha256 == second.output_sha256
        newbase = f"/api/v1/projects/{restored.json()['handle']}"
        verification = client.post(newbase + f"/jobs/{job.id}/verify", headers=headers, json={})
        assert verification.status_code == 200, verification.text
        assert (
            client.get(newbase + f"/jobs/{job.id}/video").content
            == (item.assets.store.root / job.destination).read_bytes()
        )
