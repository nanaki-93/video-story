import pytest
from test_web_service import connect
from test_web_service import workspace as workspace

from tabi.core.flow.service import FlowService
from tabi.core.models.flow import FlowLimits, FlowRecipe
from tabi.core.persistence import ProjectBusy


def setup(workspace):
    runtime, client, origin, _ = workspace
    _, headers, _ = connect(runtime, client, origin)
    opened = client.post(
        "/api/v1/projects/open", json={"root_id": "work", "path": "Test project"}, headers=headers
    ).json()
    base = f"/api/v1/projects/{opened['handle']}/flow"
    limits = FlowLimits(
        credit_ceiling=70,
        remaining_allowance=100,
        estimated_credit_per_attempt=5,
        allowance_checked_at="2026-10-06",
    )
    return runtime, client, headers, opened, base, limits


def test_flow_next_step_reuses_prompt_pause_clone_and_stale_revision(workspace):
    runtime, client, headers, opened, base, limits = setup(workspace)
    result = client.post(
        base,
        json={
            "limits": limits.model_dump(),
            "recipe": FlowRecipe(opening_mode="text_reference").model_dump(mode="json"),
        },
        headers=headers,
    )
    assert result.status_code == 200, result.text
    data = result.json()
    path = base + "/" + data["episode"]["id"]
    assert data["next_step"]["action"] == "prepare"
    result = client.post(path + "/prepare", json={"expected_revision": 0}, headers=headers)
    assert result.status_code == 200, result.text
    current = result.json()["episode"]
    assert result.json()["next_step"]["action"] == "waiting_flow"
    assert (
        client.post(
            path + "/prepare", json={"expected_revision": current["revision"]}, headers=headers
        ).json()["episode"]
        == current
    )
    assert (
        client.post(path + "/pause", json={"expected_revision": 0}, headers=headers).status_code
        == 409
    )
    assert (
        client.post(
            path + "/pause", json={"expected_revision": current["revision"]}, headers=headers
        ).json()["next_step"]["action"]
        == "paused"
    )
    clone = client.post(path + "/clone", json={"title": "New outfit"}, headers=headers).json()[
        "episode"
    ]
    assert not clone["attempts"] and not clone["accepted_ids"]
    service = FlowService(runtime.get(opened["handle"]).assets.store)
    assert len(service.list()) == 2


def test_flow_security_strict_input_registered_roots_and_one_media_lane(workspace):
    runtime, client, headers, opened, base, limits = setup(workspace)
    assert client.post(base, json={"limits": limits.model_dump()}).status_code == 403
    assert (
        client.post(
            base, json={"limits": limits.model_dump(), "credential": "never"}, headers=headers
        ).status_code
        == 422
    )
    result = client.post(base, json={"limits": limits.model_dump()}, headers=headers).json()
    path = base + "/" + result["episode"]["id"]
    assert result["next_step"]["action"] == "choose_reference"
    item = runtime.get(opened["handle"])
    with runtime.local_operation(item):
        with pytest.raises(ProjectBusy):
            with runtime.local_operation(item):
                pass
        response = client.post(
            path + "/reference",
            json={"expected_revision": 0, "source": {"root_id": "work", "path": "missing.png"}},
            headers=headers,
        )
        assert response.status_code == 409
    client.cookies.clear()
    assert client.get(path).status_code == 401
    assert client.get(path + "/references/0").status_code == 401


def test_flow_cancel_refuses_another_workers_owner(workspace, monkeypatch):
    from types import SimpleNamespace

    from fastapi import HTTPException

    runtime, _, _, opened, _, _ = setup(workspace)
    service = SimpleNamespace(
        get_export=lambda _: SimpleNamespace(state="running", owner="another-worker")
    )
    monkeypatch.setattr(runtime, "flow_service", lambda _: service)
    with pytest.raises(HTTPException) as error:
        runtime.flow_cancel(runtime.get(opened["handle"]), "foreign")
    assert error.value.status_code == 409
