import hashlib
import io

from PIL import Image
from test_web_service import connect
from test_web_service import workspace as _workspace

from tabi.api.runtime import Runtime
from tabi.api.uploads import Uploads
from tabi.core.authoring import AuthoringService
from tabi.core.fixtures import generate_fixtures
from tabi.core.models.base import AssetRef

workspace = _workspace


def test_editor_http_roundtrip_validation_and_stale_client(workspace):
    runtime, client, origin, _ = workspace
    generate_fixtures(runtime.roots.root("work") / "Editor")
    _, headers, _ = connect(runtime, client, origin)
    project = client.post(
        "/api/v1/projects/open", headers=headers, json={"root_id": "work", "path": "Editor"}
    ).json()
    base = f"/api/v1/projects/{project['handle']}/episodes/episode.synthetic"
    view = client.get(base + "/editor")
    assert view.status_code == 200, view.text
    assert view.json()["validation"]["valid"]
    assert len(view.json()["lanes"]) == 7
    result = client.post(
        base + "/edit",
        headers=headers,
        json={"expected_revision": 0, "command": {"kind": "title", "title": "HTTP edited"}},
    )
    assert result.status_code == 200 and result.json()["revision"] == 1
    stale = client.post(
        base + "/edit",
        headers=headers,
        json={"expected_revision": 0, "command": {"kind": "title", "title": "Stale"}},
    )
    assert stale.status_code == 409
    original = view.json()["episode"]
    restored = client.post(
        base + "/edit",
        headers=headers,
        json={"expected_revision": 1, "command": {"kind": "replace", "episode": original}},
    )
    assert restored.status_code == 200 and restored.json()["title"] == original["title"]


def opened(workspace):
    runtime, client, origin, _ = workspace
    _, headers, _ = connect(runtime, client, origin)
    result = client.post(
        "/api/v1/projects/create",
        headers=headers,
        json={
            "root_id": "work",
            "parent": "",
            "folder": "New 東京",
            "title": "Synthetic UI test",
        },
    )
    assert result.status_code == 200, result.text
    return runtime, client, headers, result.json(), f"/api/v1/projects/{result.json()['handle']}"


def png():
    buffer = io.BytesIO()
    Image.new("RGBA", (320, 180), (20, 40, 80, 255)).save(buffer, "PNG")
    return buffer.getvalue()


def upload(client, headers, base, data):
    result = client.post(
        base + "/uploads",
        headers=headers,
        json={
            "name": "Synthetic 東京.png",
            "size_bytes": len(data),
        },
    )
    assert result.status_code == 200, result.text
    identity = result.json()["id"]
    binary = {**headers, "Content-Type": "application/octet-stream"}
    result = client.put(f"{base}/uploads/{identity}/chunk?offset=0", content=data, headers=binary)
    assert result.status_code == 200, result.text
    return identity


def imported(client, headers, base, identity):
    result = client.post(
        base + "/uploads/import",
        headers=headers,
        json={
            "uploads": [identity],
            "request": {
                "id": "synthetic-background",
                "version": "1.0",
                "kind": "still",
                "provenance": {"origin": "synthetic", "commercial_use": "pending"},
            },
        },
    )
    assert result.status_code == 200, result.text
    return result.json()


def test_project_upload_inspect_episode_reopen_and_revision_conflict(workspace):
    runtime, client, headers, project, base = opened(workspace)
    data = png()
    identity = upload(client, headers, base, data)
    asset = imported(client, headers, base, identity)
    media = f"{base}/assets/{asset['id']}/1.0"
    assert client.get(media + "/media").content == data
    assert client.get(media + "/media", headers={"Range": "bytes=0-3"}).content == data[:4]
    health = client.get(media + "/health").json()
    assert health["media_valid"] and not health["publication_ready"]
    assert (
        client.post(
            media + "/approve",
            headers=headers,
            json={
                "expected_hash": health["content_sha256"],
                "reviewer": "Test",
                "note": "Synthetic rejection",
            },
        ).status_code
        == 400
    )
    template = client.post(
        base + "/templates/still",
        headers=headers,
        json={
            "id": "still-scene",
            "asset": {"id": asset["id"], "version": "1.0"},
        },
    )
    assert template.status_code == 200, template.text
    episode = client.post(
        base + "/episodes",
        headers=headers,
        json={
            "id": "draft",
            "title": "A synthetic scene",
            "fps": {"num": 30, "den": 1},
            "canvas": {"width": 320, "height": 180},
            "duration_frames": 60,
            "template": {"id": "still-scene", "version": "1.0"},
        },
    )
    assert episode.status_code == 200, episode.text
    document = episode.json()
    document["title"] = "Edited locally"
    saved = client.post(
        base + "/documents",
        headers=headers,
        json={
            "document": document,
            "expected_revision": 0,
        },
    )
    assert saved.status_code == 200 and saved.json()["revision"] == 1
    assert (
        client.post(
            base + "/documents",
            headers=headers,
            json={
                "document": document,
                "expected_revision": 0,
            },
        ).status_code
        == 409
    )
    listing = client.get(base + "/catalog").json()
    assert listing["episodes"][0]["title"] == "Edited locally"
    assert len(listing["assets"]) == len(listing["templates"]) == 1
    result = client.post(
        "/api/v1/projects/open",
        headers=headers,
        json={
            "root_id": "work",
            "path": "New 東京",
            "expected_project_id": project["project"]["id"],
        },
    )
    assert result.json()["handle"] == project["handle"]
    assert (
        client.post(
            "/api/v1/projects/open",
            headers=headers,
            json={
                "root_id": "work",
                "path": "Test project",
                "expected_project_id": project["project"]["id"],
            },
        ).status_code
        == 400
    )
    # Removing owned staging never removes an imported source.
    assert (
        client.post(f"{base}/uploads/{identity}/discard", headers=headers, json={}).status_code
        == 200
    )
    assert client.get(media + "/media").content == data
    item = runtime.get(project["handle"])
    assert item.jobs.ledger.all() == []
    assert len(AuthoringService(item.assets).episodes()) == 1
    restarted = Runtime(runtime.settings, runtime.roots.roots)
    assert restarted.recents().projects[0].id == project["project"]["id"]
    restored = restarted.open("work", "New 東京", project["project"]["id"])
    assert restored.info().project.title == "Synthetic UI test"
    assert len(AuthoringService(restored.assets).episodes()) == 1


def test_upload_resume_checks_bytes_offsets_size_and_complete_hash(workspace):
    runtime, client, headers, project, base = opened(workspace)
    body = b"small synthetic upload"
    start = client.post(
        base + "/uploads", headers=headers, json={"name": "file.png", "size_bytes": len(body)}
    ).json()
    route = f"{base}/uploads/{start['id']}"
    binary = {**headers, "Content-Type": "application/octet-stream"}
    assert (
        client.put(route + "/chunk?offset=0", headers=binary, content=body[:7]).status_code == 200
    )
    assert client.post(route + "/finish", headers=headers, json={}).status_code == 400
    assert (
        client.put(route + "/chunk?offset=8", headers=binary, content=body[8:]).status_code == 409
    )
    assert (
        client.put(route + "/chunk?offset=0", headers=binary, content=b"changed").status_code == 400
    )
    assert (
        client.put(route + "/chunk?offset=0", headers=binary, content=body[:7]).status_code == 200
    )
    assert (
        client.put(route + "/chunk?offset=7", headers=binary, content=body[7:]).status_code == 200
    )
    completed = client.post(route + "/finish", headers=headers, json={}).json()
    assert completed["complete"] and completed["sha256"] == hashlib.sha256(body).hexdigest()
    # Receipts survive a worker/service restart; no in-memory upload state is needed.
    copies = Uploads(runtime.get(project["handle"]).assets.store)
    assert copies.read(start["id"]).complete
    path = copies.store.root / copies.location(start["id"]).path
    path.write_bytes(b"x" * len(body))
    assert client.post(route + "/finish", headers=headers, json={}).status_code == 400


def test_upload_route_auth_limits_and_metadata_cannot_escape_or_approve(workspace):
    _, client, headers, _, base = opened(workspace)
    for name in ("../file.png", "/file.png", "directory/file.png", "upload.json"):
        assert client.post(
            base + "/uploads", headers=headers, json={"name": name, "size_bytes": 1}
        ).status_code in {400, 422}
    identity = upload(client, headers, base, png())
    route = f"{base}/uploads/{identity}/chunk?offset=0"
    assert (
        client.put(
            route,
            content=b"x",
            headers={"Origin": headers["Origin"], "Content-Type": "application/octet-stream"},
        ).status_code
        == 403
    )
    assert (
        client.put(
            route,
            content=b"x",
            headers={
                **headers,
                "Content-Type": "application/octet-stream",
                "Content-Length": str(4 * 1024**2 + 1),
            },
        ).status_code
        == 413
    )
    assert (
        client.post(
            base + "/uploads/import",
            headers=headers,
            json={"uploads": [identity], "request": {"paths": []}},
        ).status_code
        == 400
    )
    assert (
        client.post(
            base + "/documents",
            headers=headers,
            json={"document": {"schema_version": "2.0", "document_type": "episode"}},
        ).status_code
        == 422
    )


def test_asset_versions_proxies_relink_and_hash_bound_approval(workspace):
    runtime, client, headers, project, base = opened(workspace)
    data = png()
    identity = upload(client, headers, base, data)
    asset = imported(client, headers, base, identity)
    route = base + "/assets/synthetic-background/1.0"
    revised = client.post(
        route + "/version",
        headers=headers,
        json={
            "version": "1.1",
            "provenance": asset["provenance"],
            "compatibility": asset["compatibility"],
        },
    )
    assert revised.status_code == 200, revised.text
    assert revised.json()["approval"]["status"] == "draft"
    proxy = client.post(route + "/proxy", headers=headers, json={"version": "1.2", "max_edge": 80})
    assert proxy.status_code == 200, proxy.text
    image = Image.open(
        io.BytesIO(client.get(base + "/assets/synthetic-background/1.2/media?proxy=true").content)
    )
    assert image.size == (80, 45)
    item = runtime.get(project["handle"])
    old_path = item.assets.resolve(
        item.assets.load(AssetRef(id=asset["id"], version="1.0")).files[0].location
    )
    new_path = runtime.roots.root("work") / "moved.png"
    old_path.rename(new_path)
    assert not client.get(route + "/health").json()["media_valid"]
    relinked = client.post(
        route + "/relink",
        headers=headers,
        json={"version": "1.3", "paths": [{"root_id": "work", "path": "moved.png"}]},
    )
    assert relinked.status_code == 200, relinked.text
    assert client.get(base + "/assets/synthetic-background/1.3/media").content == data
    assert new_path.read_bytes() == data
    # Synthetic remains synthetic in all inherited versions, including relink/proxy records.
    assert all(
        a["provenance"]["origin"] == "synthetic"
        for a in client.get(base + "/catalog").json()["assets"]
    )
