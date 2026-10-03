import copy
import json
from fractions import Fraction
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator
from pydantic import ValidationError

from tabi.core.documents import (
    DocumentError,
    parse_document,
    schema_documents,
    validate_data,
)
from tabi.core.models import DOCUMENT_MODELS, RenderJob
from tabi.core.models.base import FrameRate, MediaPath, canonical_bytes, content_hash

EXAMPLES = Path(__file__).resolve().parents[2] / "examples"


@pytest.mark.parametrize("path", sorted(EXAMPLES.glob("*.json")), ids=lambda p: p.name)
def test_examples_validate_against_python_and_exported_json_schema(path):
    data = json.loads(path.read_text())
    document = validate_data(data)
    schema = schema_documents()[f"{data['document_type']}.schema.json"]
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(data)
    assert parse_document(canonical_bytes(document)) == document


def test_all_nested_model_schemas_reject_unknown_fields():
    for schema in schema_documents().values():
        Draft202012Validator.check_schema(schema)
        for node in [schema, *schema.get("$defs", {}).values()]:
            if node.get("type") == "object" and "properties" in node:
                assert node["additionalProperties"] is False


@pytest.mark.parametrize(
    "location",
    [
        [],
        ["fps"],
        ["scenes", 0],
        ["scenes", 0, "initial_state"],
        ["tracks", 0, "asset"],
        ["curves", 0, "keys", 0],
    ],
)
def test_nested_unknown_fields_are_reported_at_their_location(episode_data, location):
    item = episode_data
    for part in location:
        item = item[part]
    item["typo"] = "should not be silently ignored"
    with pytest.raises(DocumentError) as error:
        validate_data(episode_data)
    assert any(issue.location == [*location, "typo"] for issue in error.value.issues)


@pytest.mark.parametrize("value", [True, 1.5, "3600", -1, 0])
def test_frames_are_strict_integers(episode_data, value):
    episode_data["duration_frames"] = value
    with pytest.raises(DocumentError):
        validate_data(episode_data)


@pytest.mark.parametrize("version", ["2.0", "0.9", "1.9", "1", 1.0, None])
def test_versions_are_never_silently_coerced_or_migrated(project_data, version):
    project_data["schema_version"] = version
    with pytest.raises(DocumentError) as error:
        validate_data(project_data)
    assert error.value.code == "unsupported_schema_version"


@pytest.mark.parametrize("num,den", [(30, 1), (30000, 1001), (96000, 1)])
def test_sample_boundaries_use_exact_ties_to_even(num, den):
    fps = FrameRate(num=num, den=den)
    for frame in [0, 1, 2, 3, 999, 1000000001]:
        assert fps.sample_at(frame) == round(Fraction(frame * 48000 * den, num))
    if num == 96000:
        assert fps.sample_at(1) == 0
        assert fps.sample_at(3) == 2


@pytest.mark.parametrize("num,den", [(True, 1), (30, 0), (60, 2), (29.97, 1)])
def test_frame_rate_requires_reduced_integer_rational(num, den):
    with pytest.raises(ValidationError):
        FrameRate(num=num, den=den)


@pytest.mark.parametrize(
    "path",
    [
        "../source.png",
        "/tmp/source.png",
        "C:/source.png",
        "a//b.png",
        "a/./b.png",
        "a/../b.png",
        "https://host/a",
        "a\\b",
        "~/.key",
        "a\x00b",
    ],
)
def test_media_paths_reject_nonportable_and_escaping_forms(path):
    with pytest.raises(ValidationError):
        MediaPath(path=path)


def test_unicode_paths_and_yaml_have_the_same_canonical_form(project_data):
    project_data["media_roots"] = {"music": "/Volumes/音楽 drive"}
    json_document = validate_data(project_data)
    yaml_document = parse_document(yaml.safe_dump(project_data, allow_unicode=True), format="yaml")
    assert canonical_bytes(json_document) == canonical_bytes(yaml_document)
    assert MediaPath(path="assets/東京 scene.png").path == "assets/東京 scene.png"


@pytest.mark.parametrize(
    "payload,format",
    [
        ('{"schema_version":"1.0","schema_version":"2.0"}', "json"),
        ('{"bad":NaN}', "json"),
        ('schema_version: "1.0"\nschema_version: "2.0"', "yaml"),
        ('!!python/object/apply:os.system ["echo forbidden"]', "yaml"),
        ("x: &x [1]\ny: *x", "yaml"),
        ("[1,2,3]", "json"),
        ("1: value", "yaml"),
    ],
)
def test_ambiguous_or_unsafe_documents_fail(payload, format):
    with pytest.raises(DocumentError):
        parse_document(payload, format=format)


def test_scene_gaps_and_undeclared_overlaps_fail(episode_data):
    second = copy.deepcopy(episode_data["scenes"][0])
    second.update(id="train-02", start_frame=1800)
    episode_data["scenes"][0]["end_frame"] = 1799
    episode_data["scenes"].append(second)
    episode_data.update(actions=[], curves=[], events=[])
    with pytest.raises(DocumentError, match="structural"):
        validate_data(episode_data)
    episode_data["scenes"][0]["end_frame"] = 1801
    with pytest.raises(DocumentError):
        validate_data(episode_data)
    episode_data["scenes"][0]["end_frame"] = 1800
    validate_data(episode_data)


def test_overlap_requires_matched_duration_and_character_policy(episode_data):
    episode_data.update(actions=[], curves=[], events=[])
    first = episode_data["scenes"][0]
    second = copy.deepcopy(first)
    second.update(id="train-02", start_frame=1755)
    first["end_frame"] = 1800
    transition = {
        "kind": "overlap",
        "overlap_frames": 45,
        "character_policy": "single_visible",
        "note": "An authored transition to the next environment.",
    }
    first["transition_out"] = transition
    second["transition_in"] = transition
    episode_data["scenes"].append(second)
    validate_data(episode_data)
    second["transition_in"] = {**transition, "overlap_frames": 44}
    with pytest.raises(DocumentError):
        validate_data(episode_data)


def test_duplicate_ids_conflicts_and_out_of_scope_events_fail(episode_data):
    bad = copy.deepcopy(episode_data)
    bad["actions"][1]["start_frame"] = 899
    with pytest.raises(DocumentError):
        validate_data(bad)
    bad = copy.deepcopy(episode_data)
    bad["actions"][1]["id"] = bad["actions"][0]["id"]
    with pytest.raises(DocumentError):
        validate_data(bad)
    bad = copy.deepcopy(episode_data)
    bad["events"][0]["end_frame"] = 4000
    with pytest.raises(DocumentError):
        validate_data(bad)


def test_invalid_curves_and_audio_boundaries_fail(episode_data):
    bad = copy.deepcopy(episode_data)
    bad["curves"][0]["keys"][1]["frame"] = 0
    with pytest.raises(DocumentError):
        validate_data(bad)
    bad = copy.deepcopy(episode_data)
    bad["tracks"][0]["start_sample"] = 1
    with pytest.raises(DocumentError):
        validate_data(bad)
    bad = copy.deepcopy(episode_data)
    bad["tracks"][0]["trim_end_sample"] = 48000
    with pytest.raises(DocumentError):
        validate_data(bad)


def test_real_fixture_hash_is_recorded_and_synthetic_cannot_be_approved(asset_data):
    import hashlib

    path = EXAMPLES.parent / asset_data["files"][0]["location"]["path"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == asset_data["files"][0]["sha256"]
    asset = validate_data(asset_data)
    asset_data["approval"] = {
        "status": "approved",
        "content_sha256": asset.approval_hash,
        "reviewer": "Synthetic guard test",
        "reviewed_at": "2026-10-03T00:00:00Z",
    }
    with pytest.raises(DocumentError):
        validate_data(asset_data)


def test_approval_becomes_invalid_when_content_changes():
    raw = json.loads((EXAMPLES / "scene.train.json").read_text())
    template = validate_data(raw)
    raw["approval"] = {
        "status": "approved",
        "content_sha256": template.approval_hash,
        "reviewer": "Synthetic guard test",
        "reviewed_at": "2026-10-03T00:00:00Z",
    }
    validate_data(raw)
    raw["design_canvas"]["width"] = 3840
    with pytest.raises(DocumentError):
        validate_data(raw)


def test_snapshot_requires_every_direct_reference_to_be_hashed(snapshot_data):
    snapshot = validate_data(snapshot_data)
    assert parse_document(canonical_bytes(snapshot)) == snapshot
    snapshot_data["locked_assets"] = []
    with pytest.raises(DocumentError):
        validate_data(snapshot_data)


def test_job_progress_cannot_claim_unverified_frames(snapshot_data):
    job = {
        "schema_version": "1.0",
        "document_type": "render_job",
        "id": "job-test",
        "snapshot_sha256": content_hash(validate_data(snapshot_data)),
        "profile": {
            "id": "proxy",
            "canvas": {"width": 960, "height": 540},
            "fps": {"num": 30, "den": 1},
            "container": "mp4",
            "video_codec": "h264",
            "pixel_format": "yuv420p",
            "color_space": "bt709",
        },
        "backend": snapshot_data["compiler"],
        "state": "queued",
        "duration_frames": 3600,
        "chunks": [{"index": 0, "first_frame": 0, "frame_count": 3600, "state": "pending"}],
    }
    assert isinstance(validate_data(job), RenderJob)
    job["completed_frames"] = 3600
    with pytest.raises(DocumentError):
        validate_data(job)


def test_release_cannot_claim_upload_readiness_with_pending_rights():
    release = json.loads((EXAMPLES / "music-release.json").read_text())
    release["status"] = "ready_for_manual_upload"
    with pytest.raises(DocumentError):
        validate_data(release)


def test_python_boundary_does_not_coerce_mapping_keys(project_data):
    project_data["media_roots"] = {1: "/Volumes/music"}
    with pytest.raises(DocumentError):
        validate_data(project_data)


@pytest.mark.parametrize("repeat", [0, 1, "false", True])
def test_landmark_repeat_is_a_strict_false_boolean(episode_data, repeat):
    episode_data["events"][0]["repeat"] = repeat
    with pytest.raises(DocumentError):
        validate_data(episode_data)


def test_root_registry_is_complete(project_data, snapshot_data):
    assert {
        "audio_edit_plan",
        "preview_selection",
        "project",
        "asset",
        "episode",
        "scene_template",
        "action_pack",
        "compiled_snapshot",
        "render_job",
        "job_event",
        "release_record",
        "validation_report",
        "capability_report",
        "render_spike_report",
        "fixture_manifest",
        "asset_health",
        "render_report",
        "compilation_result",
        "audio_timeline_report",
        "waveform_report",
        "audio_mix_report",
        "storyboard_report",
        "cache_entry",
        "cache_inventory",
        "cache_prune_report",
        "storage_estimate",
        "export_verification",
        "release_preparation",
        "public_release",
        "release_inspection",
        "release_bundle_report",
    } == set(DOCUMENT_MODELS)
    for data in [project_data, snapshot_data]:
        document = validate_data(data)
        Draft202012Validator(document.model_json_schema()).validate(data)
