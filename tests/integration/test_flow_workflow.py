"""A complete assisted 90s run through the same authenticated services as the UI."""

import json
import os
import time
import wave
from pathlib import Path

import numpy as np
import pytest
from test_flow_import import accept_last, make_clip, media_context, pending

from tabi.api.launcher import OwnedWorker
from tabi.core.assets.service import digest_file
from tabi.core.flow.media import FlowMedia
from tabi.core.flow.prompts import expected_ending
from tabi.core.models.base import MediaPath
from tabi.core.models.flow import FlowBeat, FlowRecipe, FlowState
from tabi.core.process import run_tool
from tabi.core.render.ffmpeg import verify_video

pytestmark = pytest.mark.media
REPO = Path(__file__).resolve().parents[2]


def save_evidence(name, data, tmp_path):
    folder = Path(os.environ.get("TABI_FLOW_EVIDENCE_DIR", str(tmp_path)))
    folder.mkdir(parents=True, exist_ok=True)
    (folder / name).write_text(json.dumps(data, indent=2) + "\n")


def rgb_frame(settings, path, frame):
    raw = run_tool(
        [
            settings.ffmpeg,
            "-v",
            "error",
            "-nostdin",
            "-i",
            str(path),
            "-vf",
            f"select=eq(n\\,{frame})",
            "-frames:v",
            "1",
            "-pix_fmt",
            "rgb24",
            "-f",
            "rawvideo",
            "-",
        ]
    )
    return np.frombuffer(raw, dtype=np.uint8).astype(np.int16)


def exercise_90s_workflow(tmp_path, *, planned=False):
    started = time.monotonic()
    settings, sources, service, _ = media_context(tmp_path)
    original_hashes = {}
    worker = OwnedWorker(settings, {"work": tmp_path}, REPO / "web/dist")
    try:

        def open_project():
            return worker.request(
                "POST",
                "/api/v1/projects/open",
                {"root_id": "work", "path": service.store.root.relative_to(tmp_path).as_posix()},
            )

        handle = open_project()["handle"]
        base = f"/api/v1/projects/{handle}/flow"
        view = worker.request(
            "POST",
            base,
            {
                "title": "SYNTHETIC 90s planned shots"
                if planned
                else "Synthetic 90s legacy workflow",
                "recipe": None
                if planned
                else FlowRecipe(
                    beats=[
                        FlowBeat(id=kind, kind=kind, target_frame=second * 24)
                        for kind, second in [
                            ("rest", 0),
                            ("look", 15),
                            ("pickup", 30),
                            ("sip", 38),
                            ("return_cup", 45),
                            ("sway", 52),
                            ("deep_breath", 75),
                        ]
                    ]
                ).model_dump(mode="json"),
                "limits": {
                    "credit_ceiling": 0,
                    "remaining_allowance": 0,
                    "estimated_credit_per_attempt": 0,
                    "allowance_checked_at": "2026-10-06 synthetic; no provider submission",
                },
            },
        )
        path = base + "/" + view["episode"]["id"]
        state = FlowState(
            cup_kind="takeaway",
            cup_position="table",
            has_handle=False,
            has_saucer=False,
            hands="resting",
            pose="watching",
            inventory=["takeaway cup", "open book", "pen"],
        )
        keys = (
            [shot["reference_key"] for shot in view["episode"]["recipe"]["shots"]]
            if planned
            else [None]
        )
        for index, key in enumerate(keys):
            reference = sources / f"Synthetic reference {key or 'opening'}.png"
            run_tool(
                [
                    settings.ffmpeg,
                    "-v",
                    "error",
                    "-nostdin",
                    "-f",
                    "lavfi",
                    "-i",
                    "testsrc2=size=96x54:rate=24",
                    "-vf",
                    f"hue=h={index * 40}",
                    "-frames:v",
                    "1",
                    str(reference),
                ]
            )
            original_hashes[reference] = digest_file(reference)
            assert view["next_step"]["action"] == "choose_reference"
            body = {
                "expected_revision": view["episode"]["revision"],
                "source": {"root_id": "work", "path": reference.relative_to(tmp_path).as_posix()},
                "synthetic": True,
            }
            if planned:
                assert view["next_reference_key"] == key
                body.update(
                    key=key,
                    title=f"Synthetic {key}",
                    starting_state=state.model_dump(),
                    review_note="Synthetic reference only; no character approval",
                )
            view = worker.request("POST", path + "/reference", body)
        index = 0
        retried = False
        reopened = False
        while view["next_step"]["action"] != "finish":
            assert index < 15, view["next_step"]
            view = worker.request(
                "POST", path + "/prepare", {"expected_revision": view["episode"]["revision"]}
            )
            attempt = view["episode"]["attempts"][-1]
            if index == 5 and not reopened:
                view = worker.request(
                    "POST",
                    path + f"/attempts/{attempt['id']}",
                    {
                        "expected_revision": view["episode"]["revision"],
                        "state": "unknown",
                        "diagnostic": "Synthetic browser disconnect after handoff",
                    },
                )
                worker.stop()
                worker = OwnedWorker(settings, {"work": tmp_path}, REPO / "web/dist")
                assert open_project()["handle"] == handle
                restored = worker.request("GET", path)
                assert restored["next_step"]["attempt_id"] == attempt["id"]
                assert len(restored["episode"]["attempts"]) == len(view["episode"]["attempts"])
                view = restored
                reopened = True
            if planned:
                shot = next(
                    s for s in view["episode"]["recipe"]["shots"] if s["id"] == attempt["shot_id"]
                )
                assert shot["exterior"] in attempt["prompt"]
                assert all(
                    other["exterior"] not in attempt["prompt"]
                    for other in view["episode"]["recipe"]["shots"]
                    if other["id"] != shot["id"]
                )
                # Exercise an oversized native result at the first shot's exact safe outpoint.
                frames = 192 if attempt["mode"] == "shot_start" or index == 1 else 168
                if attempt["mode"] == "shot_start":
                    slot = next(
                        s
                        for s in view["reference_slots"]
                        if s["key"] == view["starting_reference_key"]
                    )
                    assert slot["url"] and "supplied clean starting image" in attempt["prompt"]
                    state = FlowState.model_validate(slot["starting_state"])
            else:
                frames = min(
                    192, view["next_step"]["target_frames"] - view["next_step"]["accepted_frames"]
                )
            clip = sources / f"clip {index} 東京.mp4"
            make_clip(settings, clip, frames=frames, hue=index * 7)
            original_hashes[clip] = digest_file(clip)
            view = worker.request(
                "POST",
                path + "/import",
                {
                    "expected_revision": view["episode"]["revision"],
                    "attempt_id": attempt["id"],
                    "source": {"root_id": "work", "path": clip.relative_to(tmp_path).as_posix()},
                    "synthetic": True,
                    "provider_model": "Synthetic fixture; no Google generation",
                },
            )
            candidate = view["episode"]["candidates"][-1]
            if planned:
                assert "Planned window view: " + shot["exterior"] in view["review"]["checklist"]
                assert any("Level horizon" in check for check in view["review"]["checklist"])
            if planned and attempt["parent_id"]:
                assert view["review"]["join_url"]
                kind = "camera cut" if attempt["mode"] == "shot_start" else "continuation"
                assert f'join_kind: "{kind}"' in view["review"]["diagnostics"]
            if planned and index == 1:
                assert view["safe_cut_frame"] == 168
                assert any(i["frame"] == 167 for i in view["review"]["images"])
            body = {
                "expected_revision": view["episode"]["revision"],
                "media_sha256": candidate["media"]["sha256"],
                "decision": "accepted",
                "note": "Synthetic state/timing test only; not publication approval",
            }
            if index == 2 and not retried:
                body.update(
                    decision="rejected",
                    retry_focus="particles" if planned else None,
                    note="Synthetic dots and mouth mismatch; full history stays out of the prompt",
                )
                retried = True
            else:
                state = expected_ending(state, FlowBeat.model_validate(attempt["beat"]))
                body.update(
                    observed_state=state.model_dump(mode="json"),
                    safe_end_frame=view["safe_cut_frame"],
                )
            view = worker.request("POST", path + f"/clips/{candidate['id']}/review", body)
            index += 1
        assert view["next_step"]["accepted_frames"] == 2160
        assert not view["remaining_beats"] and retried and reopened
        if planned:
            assert all(s["state"] == "complete" for s in view["shots"])
            assert [s["accepted_frames"] for s in view["shots"]] == [360] * 6
            assert len({r["media"]["sha256"] for r in view["episode"]["references"]}) == 6
            retry = view["episode"]["attempts"][3]
            assert retry["mode"] == "shot_start" and retry["shot_id"] == "yanaka"
            assert "Carriage air stays clear" in retry["prompt"]
            assert "full history" not in retry["prompt"] and "full history" in retry["retry_reason"]
            assert retry["references_sha256"] == view["episode"]["attempts"][2]["references_sha256"]
        source = sources / "Synthetic master.wav"
        samples = (np.sin(np.arange(4320000) * 2 * np.pi * 220 / 48000) * 1000).astype("<i2")
        with wave.open(str(source), "wb") as output:
            output.setnchannels(1)
            output.setsampwidth(2)
            output.setframerate(48000)
            output.writeframes(samples.tobytes())
        original = source.read_bytes()
        view = worker.request(
            "POST",
            path + "/music/import",
            {
                "expected_revision": view["episode"]["revision"],
                "source": {"root_id": "work", "path": source.relative_to(tmp_path).as_posix()},
                "synthetic": True,
            },
        )
        asset = view["audio_sources"][0]["asset"]
        view = worker.request(
            "POST",
            path + "/exports",
            {
                "expected_revision": view["episode"]["revision"],
                "tracks": [
                    {
                        "id": "music",
                        "asset": {"id": asset["id"], "version": asset["version"]},
                        "start_sample": 0,
                        "trim_start_sample": 0,
                        "trim_end_sample": 4320000,
                    }
                ],
            },
        )
        identity = view["exports"][-1]["id"]
        deadline = time.monotonic() + 120
        while time.monotonic() < deadline:
            view = worker.request("GET", path)
            export = next(e for e in view["exports"] if e["id"] == identity)
            assert export["state"] not in {"failed", "cancelled"}, export["diagnostic"]
            if export["state"] == "verified":
                break
            time.sleep(0.1)
        assert export["state"] == "verified"
        frozen = service.get_export(identity)
        verified = verify_video(
            settings, service.verify_file(frozen.output), frozen.inputs.profile, 2160
        )
        report = json.loads(service.store._read_bytes(frozen.report_path))
        assert verified.duration_seconds == 90
        assert report["audio"]["verification"]["intended_samples"] == 4320000
        assert report["synthetic"] and report["creative_approval"] == "pending"
        assert source.read_bytes() == original
        assert all(digest_file(p) == value for p, value in original_hashes.items())
        assert len(view["episode"]["accepted_ids"]) == 12 and len(view["episode"]["attempts"]) == 13
        offset = 0
        comparisons = 0
        for index, segment in enumerate(frozen.inputs.segments):
            count = segment.trim.end_frame - segment.trim.start_frame
            # Compare both sides of all eleven joins to the actual frozen sources.
            boundaries = []
            if index:
                boundaries.append((offset, segment.trim.start_frame))
            if index < len(frozen.inputs.segments) - 1:
                boundaries.append((offset + count - 1, segment.trim.end_frame - 1))
            for output_frame, source_frame in boundaries:
                difference = np.abs(
                    rgb_frame(settings, service.verify_file(frozen.output), output_frame)
                    - rgb_frame(settings, service.verify_file(segment.media), source_frame)
                )
                assert np.mean(difference) < 4
                comparisons += 1
            offset += count
        assert offset == 2160 and comparisons == 22
        delivery = worker.request(
            "POST",
            f"/api/v1/projects/{handle}/releases",
            {
                "preparation": {
                    "schema_version": "1.0",
                    "id": "flow-test-release",
                    "source_kind": "flow",
                    "job_id": identity,
                    "title": "SYNTHETIC: not for publication",
                },
                "expected_revision": None,
            },
        )
        inspection = worker.request(
            "POST", f"/api/v1/projects/{handle}/releases/{delivery['id']}/inspect", {}
        )
        assert "synthetic_assets" in inspection["blockers"]
        save_evidence(
            "shot-workflow.json" if planned else "synthetic-workflow.json",
            {
                "project_path": str(service.store.root),
                "episode_id": view["episode"]["id"],
                "export_id": frozen.id,
                "output_path": str(service.verify_file(frozen.output)),
                "planned_shots": view["shots"],
                "fresh_starts": sum(a["mode"] == "shot_start" for a in view["episode"]["attempts"]),
                "duration_frames": 2160,
                "fps": {"num": 24, "den": 1},
                "duration_seconds": 90,
                "accepted_clips": 12,
                "attempts": 13,
                "rejected_clips": 1,
                "reopen_pending_attempt": True,
                "samples": 4320000,
                "output_sha256": frozen.output.sha256,
                "source_audio_unchanged": True,
                "all_frames_and_pts": "strict full decode verified",
                "source_hashes_rechecked": True,
                "join_boundaries_compared": comparisons,
                "creative_approval": "pending",
                "production_blockers": inspection["blockers"],
                "external_generation_requests": 0,
                "elapsed_seconds": round(time.monotonic() - started, 2),
            },
            tmp_path,
        )
    finally:
        worker.stop(cancel=True)


def test_legacy_90s_recipe_reject_retry_unknown_reopen_local_music_and_exact_export(tmp_path):
    exercise_90s_workflow(tmp_path)


def test_actual_tokyo_native_import_has_no_inherited_hold_and_keeps_visual_gate(tmp_path):
    location = os.environ.get("TABI_TOKYO_SOURCE")
    if not location:
        pytest.skip("Actual private Tokyo files are optional; provide TABI_TOKYO_SOURCE")
    source = Path(location).resolve()
    settings, _, service, episode = media_context(tmp_path, target=528)
    service.media_roots = {"source": source}
    hashes = []
    from tabi.core.assets.service import digest_file

    for index, count in enumerate((192, 168, 168), start=1):
        path = source / f"clip-{index:02}.mp4"
        original = digest_file(path)
        episode = pending(service, episode)
        episode = FlowMedia(service, settings).import_result(
            episode.id,
            episode.attempts[-1].id,
            MediaPath(root_id="source", path=path.name),
            revision=episode.revision,
        )
        assert episode.candidates[-1].frame_count == count and digest_file(path) == original
        hashes.append(original[0])
        if index < 3:
            # Only engineering lineage for existing clips; no production creative approval.
            episode = accept_last(service, episode)
    assert sum(c.frame_count for c in episode.candidates) == 528
    assert episode.candidates[-1].review == "pending"
    save_evidence(
        "tokyo-native-import.json",
        {
            "source_frames": [192, 168, 168],
            "total_frames": 528,
            "fps": {"num": 24, "den": 1},
            "native_duration_seconds": 22,
            "one_second_scene_hold": "absent in native clip imports; every PTS verified",
            "source_sha256": hashes,
            "originals_unchanged": True,
            "third_clip_visual_gate": "pending: invented saucer and floating particles",
            "credits_consumed": 0,
            "new_generation": False,
        },
        tmp_path,
    )
