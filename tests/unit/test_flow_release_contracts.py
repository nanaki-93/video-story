from datetime import UTC, datetime

import pytest

from tabi.core.models.publishing import FlowCommercialReview, ReleasePreparation


def test_legacy_preparation_keeps_identical_serialized_fields():
    original = {
        "schema_version": "1.0",
        "document_type": "release_preparation",
        "revision": 0,
        "id": "legacy",
        "job_id": "job",
        "title": "Same",
        "description": "",
        "disclosure_notes": "",
        "chapters": [],
        "thumbnail": None,
        "creative_review": None,
        "metadata_review": None,
    }
    assert ReleasePreparation.model_validate(original).model_dump(mode="json") == original
    flow = ReleasePreparation.model_validate({**original, "source_kind": "flow"})
    assert flow.model_dump(mode="json")["source_kind"] == "flow"


def test_flow_terms_are_dated_model_specific_official_evidence():
    review = {
        "provider_models": ["Veo test fixture (not a licence assertion)"],
        "commercial_use": "pending",
        "reviewed_at": datetime.now(UTC),
        "reviewer": "Unit test",
        "source_links": ["https://support.google.com/flow/answer/16353333?hl=en"],
        "note": "Pending, no approval",
    }
    assert FlowCommercialReview.model_validate(review).commercial_use == "pending"
    for changes in (
        {"provider_models": []},
        {"source_links": ["https://example.com/terms"]},
        {"api_key": "never"},
    ):
        with pytest.raises(ValueError):
            FlowCommercialReview.model_validate({**review, **changes})
