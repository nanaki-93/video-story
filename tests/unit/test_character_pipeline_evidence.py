import copy

import pytest
from PIL import Image
from pydantic import ValidationError

from scripts.verify_character_pipeline import REQUIRED_GATES, Report, digest, verify


@pytest.fixture
def evidence(tmp_path):
    master = tmp_path / "test-only master.bin"
    master.write_bytes(b"synthetic test master, not artwork")
    image = tmp_path / "review 東京.png"
    Image.new("RGBA", (32, 24), (10, 20, 30, 255)).save(image)
    data = {
        "schema_version": "1.0",
        "task_id": "P01",
        "review_date": "2026-10-05",
        "decision": "no_go",
        "decision_scope": "Synthetic verifier fixture",
        "production_ready": False,
        "user_visual_approval": "pending",
        "summary": "This fixture cannot approve art.",
        "master_sha256": digest(master),
        "artifacts": [
            {"path": master.name, "sha256": digest(master), "kind": "file", "role": "master"},
            {
                "path": image.name,
                "sha256": digest(image),
                "kind": "image",
                "role": "render",
                "width": 32,
                "height": 24,
                "master_sha256": digest(master),
            },
        ],
        "gates": {
            name: {"status": "not_run", "evidence": "Not performed"} for name in REQUIRED_GATES
        },
        "licenses": [],
        "environment": {},
        "measurements": {},
        "operations": [],
        "unresolved": ["Synthetic fixture"],
        "generation_prompt": "No generation",
    }
    data["gates"]["likeness"] = {"status": "failed", "evidence": "Synthetic fixture"}
    return data, tmp_path


def test_no_go_evidence_can_be_valid_without_approving_production(evidence):
    data, root = evidence
    report = Report.model_validate(data)
    assert verify(report, root) == 2
    assert not report.production_ready


def test_changed_source_is_rejected(evidence):
    data, root = evidence
    (root / data["artifacts"][0]["path"]).write_bytes(b"changed source")
    with pytest.raises(ValueError, match="changed evidence"):
        verify(Report.model_validate(data), root)


def test_hash_match_does_not_hide_wrong_image_dimensions(evidence):
    data, root = evidence
    data["artifacts"][1]["width"] = 64
    with pytest.raises(ValueError, match="dimensions"):
        verify(Report.model_validate(data), root)


def test_missing_acceptance_case_cannot_be_silently_dropped(evidence):
    data, root = evidence
    del data["gates"]["different_garment"]
    with pytest.raises(ValueError, match="every P01"):
        verify(Report.model_validate(data), root)


def test_successful_file_checks_cannot_promote_unperformed_gates(evidence):
    data, root = evidence
    data.update(decision="go", production_ready=True)
    with pytest.raises(ValueError, match="Unperformed or unapproved"):
        verify(Report.model_validate(data), root)


def test_claimed_second_render_must_use_same_master(evidence):
    data, root = evidence
    data["artifacts"][1]["master_sha256"] = "a" * 64
    with pytest.raises(ValueError, match="Master identity"):
        verify(Report.model_validate(data), root)


def test_report_paths_are_confined_to_project(evidence):
    data, root = evidence
    data["artifacts"][0]["path"] = "../outside.bin"
    with pytest.raises(ValueError, match="escapes"):
        verify(Report.model_validate(data), root)


@pytest.mark.parametrize("update", [{"schema_version": "2.0"}, {"auto_approve": True}])
def test_unknown_versions_and_fields_are_rejected(evidence, update):
    data, _ = evidence
    invalid = copy.deepcopy(data)
    invalid.update(update)
    with pytest.raises(ValidationError):
        Report.model_validate(invalid)
