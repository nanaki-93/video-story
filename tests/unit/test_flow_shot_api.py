"""Transport coverage; unit receipts stand in for independently tested media decoding."""

import hashlib

from test_flow_shot_runner import facts, receipt
from test_web_flow_contracts import setup
from test_web_service import workspace as workspace

from tabi.core.flow.media import FlowMedia
from tabi.core.models.base import HashedFile, MediaPath
from tabi.core.models.flow import FlowBeat, FlowRecipe, FlowReference, FlowShot


def create(workspace, monkeypatch, recipe=None):
    runtime, client, headers, opened, base, limits = setup(workspace)
    item = runtime.get(opened["handle"])

    def reference(self, source, **values):
        path = item.assets.store.root / "sources" / f"{values['key']}.png"
        path.write_bytes(values["key"].encode())  # Unit storage fixture, not visual evidence.
        return FlowReference(
            **values,
            media=HashedFile(
                location=MediaPath(path=f"sources/{path.name}"),
                sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                size_bytes=path.stat().st_size,
            ),
        )

    monkeypatch.setattr(FlowMedia, "reference", reference)
    response = client.post(
        base,
        json={"limits": limits.model_dump(), "recipe": recipe.model_dump() if recipe else None},
        headers=headers,
    )
    assert response.status_code == 200, response.text
    view = response.json()
    path = base + "/" + view["episode"]["id"]
    return runtime.flow_service(item), client, headers, path, view


def upload(client, headers, path, view):
    key = view["next_reference_key"]
    response = client.post(
        path + "/reference",
        json={
            "expected_revision": view["episode"]["revision"],
            "source": {"root_id": "work", "path": "source.png"},
            "title": key,
            "key": key,
            "starting_state": facts().model_dump(),
            "review_note": "Synthetic fixture only",
            "synthetic": True,
        },
        headers=headers,
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_reference_guidance_requires_all_views_and_atomic_variation_reset(workspace, monkeypatch):
    service, client, headers, path, view = create(workspace, monkeypatch)
    assert len(view["shots"]) == 6 and view["shots"][-1]["start_frame"] == 1800
    assert view["next_reference_key"] == "wide"
    assert [b["kind"] for b in view["remaining_beats"]][2:5] == ["pickup", "sip", "return_cup"]
    for key in ("wide", "close", "medium"):
        assert view["next_reference_key"] == key
        slot = next(s for s in view["reference_slots"] if s["key"] == key)
        assert slot["url"] is None and "clear" in slot["instruction"]
        view = upload(client, headers, path, view)
    assert view["next_step"]["action"] == "prepare"
    assert all(s["url"] for s in view["reference_slots"])
    recipe = {**view["episode"]["recipe"], "outfit": "Blue coat"}
    clone = client.post(
        path + "/clone", json={"title": "Different outfit", "recipe": recipe}, headers=headers
    ).json()
    assert not clone["episode"]["references"]
    assert clone["next_step"]["action"] == "choose_reference"
    assert len(service.get(view["episode"]["id"]).references) == 3


def test_shot_review_cut_boundary_and_focused_retry_survive_api_reopen(workspace, monkeypatch):
    recipe = FlowRecipe(
        target_frames=24,
        shots=[
            FlowShot(
                id=key,
                title=key,
                reference_key=key,
                framing=key,
                duration_frames=12,
                beats=[FlowBeat(id=key, kind="rest", target_frame=0)],
            )
            for key in ("wide", "close")
        ],
    )
    service, client, headers, path, view = create(workspace, monkeypatch, recipe)
    for _ in range(2):
        view = upload(client, headers, path, view)
    identity = view["episode"]["id"]

    def prepare():
        result = client.post(
            path + "/prepare",
            json={"expected_revision": service.get(identity).revision},
            headers=headers,
        )
        assert result.status_code == 200, result.text
        return result.json()

    def result(frames):
        receipt(service, service.get(identity), frames=frames)
        return client.get(path).json()

    def review(view, **changes):
        candidate = view["episode"]["candidates"][-1]
        body = {
            "expected_revision": view["episode"]["revision"],
            "media_sha256": candidate["media"]["sha256"],
            "decision": "accepted",
            "note": "Synthetic fixture only",
            "observed_state": facts().model_dump(),
            **changes,
        }
        return client.post(path + f"/clips/{candidate['id']}/review", json=body, headers=headers)

    assert prepare()["episode"]["attempts"][-1]["mode"] == "shot_start"
    assert review(result(8)).status_code == 200
    assert prepare()["episode"]["attempts"][-1]["mode"] == "extend"
    view = result(8)
    assert view["safe_cut_frame"] == 4  # Remaining shot, not remaining whole video.
    assert review(view).status_code == 400
    assert review(view, safe_end_frame=4).status_code == 200
    view = prepare()
    assert view["parent_url"] and view["starting_reference_key"] == "close"
    assert view["episode"]["attempts"][-1]["mode"] == "shot_start"
    view = result(12)
    response = review(
        view,
        decision="rejected",
        observed_state=None,
        retry_focus="particles",
        note="Dots, mouth and hands changed. This complete note stays in history.",
    )
    assert response.status_code == 200, response.text
    view = prepare()
    attempt = view["episode"]["attempts"][-1]
    assert attempt["mode"] == "shot_start" and "complete note" not in attempt["prompt"]
    assert "clear" in attempt["prompt"] and "complete note" in attempt["retry_reason"]
    assert client.get(path).json()["episode"] == view["episode"]
    assert review(result(12), safe_end_frame=12).json()["next_step"]["action"] == "finish"


def test_reference_review_and_mutation_security_are_required(workspace, monkeypatch):
    _, client, headers, path, view = create(workspace, monkeypatch)
    payload = {"expected_revision": 0, "key": "wide", "source": {"path": "source.png"}}
    assert client.post(path + "/reference", json=payload, headers=headers).status_code == 422
    assert client.post(path + "/prepare", json={"expected_revision": 0}).status_code == 403
    view = upload(client, headers, path, view)
    assert client.get(view["reference_slots"][0]["url"]).status_code == 200
    client.cookies.clear()
    assert client.get(view["reference_slots"][0]["url"]).status_code == 401
