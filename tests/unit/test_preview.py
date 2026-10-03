from test_web_service import connect
from test_web_service import workspace as _workspace

from tabi.core.fixtures import generate_fixtures

workspace = _workspace


def test_preview_stale_revision_registry_changes_and_snapshot_notes(workspace):
    runtime, client, origin, _ = workspace
    root = runtime.roots.root("work") / "Preview 東京"
    generate_fixtures(root)
    _, headers, _ = connect(runtime, client, origin)
    opened = client.post(
        "/api/v1/projects/open", headers=headers, json={"root_id": "work", "path": root.name}
    ).json()
    base = f"/api/v1/projects/{opened['handle']}/episodes/episode.synthetic"
    route = base + "/preview"
    assert client.get(route).json()["selection"] is None
    body = {"expected_revision": 0, "first_frame": 30, "end_frame": 120}
    result = client.post(route, headers=headers, json=body)
    assert result.status_code == 200, result.text
    selection = result.json()
    view = client.get(route).json()
    assert not view["stale"] and view["job"]["duration_frames"] == 90
    assert view["job"]["first_frame"] == 30
    marker = {
        "snapshot_sha256": selection["snapshot_sha256"],
        "frame": 36,
        "note": "Synthetic frame check",
    }
    assert client.post(route + "/markers", headers=headers, json=marker).status_code == 200
    assert (
        client.post(route + "/markers", headers=headers, json={**marker, "frame": 300}).status_code
        == 400
    )
    assert (
        client.post(route + "/markers", headers=headers, json={**marker, "frame": 36.1}).status_code
        == 422
    )
    edit = {"expected_revision": 0, "command": {"kind": "title", "title": "Changed draft"}}
    assert client.post(base + "/edit", headers=headers, json=edit).status_code == 200
    view = client.get(route).json()
    assert view["stale"] and view["selection"]["job_id"] == selection["job_id"]
    assert view["snapshot_episode"]["title"] != view["episode"]["title"]
    assert client.post(route, headers=headers, json=body).status_code == 409
    assert (
        client.post(route, headers=headers, json={**body, "expected_revision": 1}).status_code
        == 200
    )
    view = client.get(route).json()
    assert not view["stale"] and view["selection"]["markers"][0]["frame"] == 36
    assert client.post(route + "/markers", headers=headers, json=marker).status_code == 409
    # Missing/changing sources do not hide the existing selection or claim freshness.
    source = next(root.rglob("*.png"))
    source.write_bytes(b"changed")
    broken = client.get(route).json()
    assert broken["stale"] and broken["issue"]
    assert broken["job"]["id"] == view["job"]["id"]
