import json
from datetime import UTC, datetime

import pytest
from test_flow_assembly import ready_video

from tabi.core.assets import AssetService
from tabi.core.flow.assembly import FlowAssembler
from tabi.core.flow.service import updated
from tabi.core.models.publishing import FlowCommercialReview, ReleasePreparation
from tabi.core.persistence import StorageError
from tabi.core.publishing import ReleaseService

pytestmark = pytest.mark.media


def test_flow_release_uses_real_export_keeps_prompts_private_and_never_approves_synthetic(tmp_path):
    settings, _, flow, episode = ready_video(tmp_path, counts=(24, 24))
    assembler = FlowAssembler(flow, settings)
    export = assembler.run(assembler.freeze(episode.id, revision=episode.revision).id)
    release = ReleaseService(
        AssetService(
            flow.store, roots=flow.media_roots, ffmpeg=settings.ffmpeg, ffprobe=settings.ffprobe
        ),
        settings,
    )
    prep = release.save(
        ReleasePreparation(
            schema_version="1.0",
            id="flow-release",
            source_kind="flow",
            job_id=export.id,
            title="Synthetic private test",
            concept_notes="Private engineering fixture",
        ),
        expected_revision=None,
    )
    inspection = release.inspect(prep)
    assert inspection.public.snapshot_sha256 == export.inputs_sha256
    assert inspection.public.frame_count == 48
    assert {
        "synthetic_assets",
        "actual_provider_model_pending",
        "flow_commercial_terms_pending_or_stale",
        "asset_rights_or_approval_pending",
    } <= set(inspection.blockers)
    with pytest.raises(StorageError, match="production creative"):
        release.review(
            prep.id,
            kind="creative",
            expected_hash=export.output.sha256,
            expected_revision=prep.revision,
            reviewer="Synthetic only",
            note="Must refuse",
        )
    with pytest.raises(StorageError, match="not ready"):
        release.export(prep.id, "must-not-publish", require_ready=True)
    reviewed = release.review(
        prep.id,
        kind="metadata",
        expected_hash=inspection.metadata_sha256,
        expected_revision=prep.revision,
        reviewer="Engineering test",
        note="Private metadata check",
    )
    assert (
        "metadata_and_disclosure_review_pending_or_stale" not in release.inspect(reviewed).blockers
    )
    terms = FlowCommercialReview(
        provider_models=["Synthetic fixture"],
        reviewed_at=datetime.now(UTC),
        reviewer="Fixture only",
        source_links=["https://support.google.com/flow/answer/16353333?hl=en"],
        note="PRIVATE-MODEL-NOTE",
    )
    changed = release.save(updated(reviewed, flow_terms=terms), expected_revision=reviewed.revision)
    assert "metadata_and_disclosure_review_pending_or_stale" in release.inspect(changed).blockers
    bundle = release.export(changed.id, "flow-draft")
    assert bundle.inspection.status == "technically_verified"
    folder = flow.store.root / bundle.bundle_path
    assert (folder / "public/video.mp4").read_bytes() == flow.verify_file(
        export.output
    ).read_bytes()
    public = "\n".join(
        p.read_text() for p in (folder / "public").iterdir() if p.suffix not in {".mp4", ".png"}
    )
    assert "PRIVATE-MODEL-NOTE" not in public and str(flow.store.root) not in public
    assert episode.attempts[0].prompt not in public
    assert (
        json.loads((folder / "private/episode-snapshot.json").read_text())["document_type"]
        == "flow_episode"
    )
    assert (folder / "private/flow-inputs.json").is_file()
    flow.verify_file(export.output).write_bytes(b"changed export")
    with pytest.raises(StorageError, match="changed"):
        release.inspect(changed)
