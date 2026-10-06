"""Transport coverage; unit receipts stand in for independently tested media decoding."""

import hashlib
import json

from test_flow_shot_runner import facts, receipt
from test_web_flow_contracts import setup
from test_web_service import workspace as workspace

from tabi.core.flow.media import FlowMedia
from tabi.core.flow.review import FlowReview
from tabi.core.flow.runner import FlowRunner
from tabi.core.flow.service import FlowError, updated
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
    keys = [shot["reference_key"] for shot in view["episode"]["recipe"]["shots"]]
    assert len(set(keys)) == 6 and view["next_reference_key"] == "sumida"
    assert {b["kind"] for b in view["remaining_beats"]} == {"rest", "look"}
    for shot in view["episode"]["recipe"]["shots"]:
        key = shot["reference_key"]
        assert view["next_reference_key"] == key
        slot = next(s for s in view["reference_slots"] if s["key"] == key)
        assert slot["url"] is None and "clear" in slot["instruction"]
        assert shot["exterior"] in slot["instruction"]
        view = upload(client, headers, path, view)
    assert view["next_step"]["action"] == "prepare"
    assert all(s["url"] for s in view["reference_slots"])
    recipe = {**view["episode"]["recipe"], "outfit": "Blue coat"}
    clone = client.post(
        path + "/clone", json={"title": "Different outfit", "recipe": recipe}, headers=headers
    ).json()
    assert not clone["episode"]["references"]
    assert clone["next_step"]["action"] == "choose_reference"
    assert len(service.get(view["episode"]["id"]).references) == 6
    scenic = view["episode"]["recipe"]
    scenic["shots"][-1]["exterior"] = "A new waterfront with a pier."
    changed_view = client.post(
        path + "/clone", json={"title": "Different closing view", "recipe": scenic}, headers=headers
    )
    assert changed_view.status_code == 200, changed_view.text
    changed = changed_view.json()
    assert changed["episode"]["references"] == view["episode"]["references"][:-1]
    assert changed["next_reference_key"] == "odaiba"


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


def test_retry_limit_recovery_is_explicit_authenticated_and_preserves_attempts(
    workspace, monkeypatch
):
    service, client, headers, path, view = create(workspace, monkeypatch)
    for _ in range(len(view["reference_slots"])):
        view = upload(client, headers, path, view)
    episode = service.get(view["episode"]["id"])
    runner = FlowRunner(service)
    for _ in range(2):
        episode = runner.prepare(episode.id, episode.revision)
        episode = runner.transition(
            episode.id,
            episode.attempts[-1].id,
            revision=episode.revision,
            state="failed",
            diagnostic="Confirmed failure",
        )
    assert client.get(path).json()["next_step"]["next_retry_limit"] == 2
    body = {"expected_revision": episode.revision}
    route = path + "/increase-retry-limit"
    assert client.post(route, json=body).status_code == 403
    result = client.post(route, json=body, headers=headers)
    assert result.status_code == 200, result.text
    current = result.json()
    assert current["next_step"]["action"] == "prepare"
    assert current["next_step"]["next_retry_limit"] is None
    assert current["episode"]["limits"]["max_retries_per_beat"] == 2
    assert current["episode"]["limits"]["credit_ceiling"] == episode.limits.credit_ceiling
    assert current["episode"]["attempts"] == episode.model_dump(mode="json")["attempts"]
    assert client.post(route, json=body, headers=headers).status_code == 400
    assert (
        client.post(
            route,
            json={"expected_revision": current["episode"]["revision"]},
            headers=headers,
        ).status_code
        == 400
    )
    assert client.get(path).json()["episode"] == current["episode"]


def test_restart_shot_route_preserves_sources_and_requires_current_authenticated_state(
    workspace, monkeypatch
):
    service, client, headers, path, view = create(workspace, monkeypatch)
    for _ in range(len(view["reference_slots"])):
        view = upload(client, headers, path, view)
    episode = service.get(view["episode"]["id"])
    runner = FlowRunner(service)
    episode = receipt(service, runner.prepare(episode.id, episode.revision), frames=192)
    candidate = episode.candidates[-1]
    episode = service.review(
        episode.id,
        candidate.id,
        revision=episode.revision,
        media_sha256=candidate.media.sha256,
        decision="accepted",
        note="Unit fixture only",
        observed_state=facts(),
    )
    assert client.get(path).json()["next_step"]["restart_shot_id"] == "sumida"
    body = {"expected_revision": episode.revision}
    route = path + "/restart-shot"
    assert client.post(route, json=body).status_code == 403
    response = client.post(route, json=body, headers=headers)
    assert response.status_code == 200, response.text
    current = response.json()
    assert not current["episode"]["accepted_ids"]
    assert current["next_step"]["action"] == "prepare"
    assert current["next_step"]["restart_shot_id"] is None
    for field in ("candidates", "attempts", "limits", "recipe", "references"):
        assert current["episode"][field] == episode.model_dump(mode="json")[field]
    assert client.post(route, json=body, headers=headers).status_code == 400
    assert (
        client.post(
            route, json={"expected_revision": current["episode"]["revision"]}, headers=headers
        ).status_code
        == 400
    )


def test_section_controls_keep_source_and_selected_playback_distinct(workspace, monkeypatch):
    service, client, headers, path, view = create(workspace, monkeypatch)
    for _ in range(len(view["reference_slots"])):
        view = upload(client, headers, path, view)
    identity = view["episode"]["id"]
    view = client.post(
        path + "/prepare",
        json={"expected_revision": view["episode"]["revision"]},
        headers=headers,
    ).json()
    episode = receipt(service, service.get(identity), frames=192)
    candidate = episode.candidates[-1]
    route = path + f"/clips/{candidate.id}/section"
    payload = {
        "expected_revision": episode.revision,
        "media_sha256": candidate.media.sha256,
        "trim": {"start_frame": 24, "end_frame": 192},
    }
    assert client.post(route, json=payload).status_code == 403
    assert (
        client.post(route, json={**payload, "expected_revision": 0}, headers=headers).status_code
        == 400
    )
    assert (
        client.post(route, json={**payload, "media_sha256": "0" * 64}, headers=headers).status_code
        == 400
    )
    assert (
        client.post(
            route, json={**payload, "trim": {"start_frame": 30, "end_frame": 20}}, headers=headers
        ).status_code
        == 422
    )
    calls = []

    def prepare(self, episode_id, candidate_id, **kwargs):
        calls.append((episode_id, candidate_id, kwargs))
        current = self.service.get(episode_id)
        if current.revision != kwargs["revision"]:
            raise FlowError("Stale request")
        clip = self.service.candidate(current, candidate_id)
        self._validate_section(current, clip, kwargs["trim"], kwargs["media_sha256"])
        packet_path = "sources/section-unit-packet.json"
        packet = {
            "candidate_sha256": clip.media.sha256,
            "candidate_trim": kwargs["trim"].model_dump(),
            "selected_video": clip.media.model_dump(mode="json"),
            "join_video": None,
            "images": [],
            "diagnostics": {"fixture": "unit transport only"},
            "review_checklist": [],
        }
        (service.store.root / packet_path).write_text(json.dumps(packet))
        return service.save(
            updated(
                current, candidates=[updated(clip, trim=kwargs["trim"], review_packet=packet_path)]
            ),
            expected_revision=current.revision,
        )

    monkeypatch.setattr(FlowReview, "prepare", prepare)
    response = client.post(route, json=payload, headers=headers)
    assert response.status_code == 200, response.text
    view = response.json()
    assert calls[0][:2] == (identity, candidate.id)
    assert view["candidate_url"].endswith("/selected")
    assert view["candidate_source_url"].endswith("/video")
    assert view["episode"]["candidates"][-1]["trim"] == payload["trim"]
    assert client.get(view["candidate_url"]).status_code == 200
    assert client.post(route, json=payload, headers=headers).status_code == 400
    assert (
        client.post(path + "/clips/foreign/section", json=payload, headers=headers).status_code
        == 400
    )
    client.cookies.clear()
    assert client.get(view["candidate_url"]).status_code == 401
