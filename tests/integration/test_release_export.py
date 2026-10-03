import json

import pytest
from test_chunk_assembly import setup

from tabi.core.assets.service import digest_file
from tabi.core.models import Episode, ReleaseRecord
from tabi.core.models.publishing import Chapter, ReleasePreparation
from tabi.core.persistence import RevisionConflict, StorageError
from tabi.core.publishing import ReleaseService
from tabi.core.timeline.compiler import ActionCompiler

pytestmark = pytest.mark.media


def test_release_copies_exact_export_keeps_private_evidence_and_rejects_stale_inputs(
    tmp_path, monkeypatch
):
    jobs, snapshot, _, profile = setup(tmp_path, "core")
    track = snapshot.audio_placements[0]
    asset = jobs.assets.load(track.asset)
    secret = "PRIVATE-LICENCE-NOTE-DO-NOT-EXPORT"
    release = ReleaseRecord(
        schema_version="1.0",
        document_type="release_record",
        id="music-test",
        artist="Synthetic test author",
        release_title="Signal, not music",
        claim_notes=secret,
        tracks=[
            {
                "asset": track.asset,
                "title": "Synthetic signal",
                "master": asset.files[0].location,
                "sha256": asset.files[0].sha256,
                "sample_rate": 48000,
                "channels": 2,
                "duration_samples": 480000,
                "credits": [{"name": "Test fixture", "role": "Synthesis"}],
                "ai_use_notes": secret,
            }
        ],
    )
    jobs.store.save_draft(release, expected_revision=None)
    episode = Episode.model_validate(
        {
            **snapshot.episode.model_dump(),
            "tracks": [
                {**item.model_dump(), "release_id": release.id}
                for item in snapshot.audio_placements
            ],
        }
    )
    snapshot = ActionCompiler(jobs.assets, purpose="synthetic_test").compile(episode)
    digest = jobs.store.save_snapshot(snapshot)
    jobs.submit(digest, profile, "exports/release.mp4", first_frame=150, end_frame=180)
    job = jobs.work()[0]
    assert job.state == "verified", job.error
    service = ReleaseService(jobs.assets, jobs.settings)
    preparation = service.save(
        ReleasePreparation(
            schema_version="1.0",
            id="release-test",
            job_id=job.id,
            title="SYNTHETIC — NOT FOR PUBLICATION",
            description="One-second engineering fixture.",
            chapters=[Chapter(start_frame=0, title="Test")],
        ),
        expected_revision=None,
    )
    inspection = service.inspect(preparation)
    assert inspection.status == "technically_verified"
    assert {"partial_export", "synthetic_assets", "music_rights_pending"} <= set(
        inspection.blockers
    )
    assert inspection.public.tracks[0].start_sample == 0
    assert inspection.public.tracks[0].end_sample == 48000
    assert inspection.public.tracks[0].isrc is inspection.public.tracks[0].upc is None
    assert inspection.public.chapter_status == "invalid"
    with pytest.raises(StorageError, match="not ready"):
        service.export(preparation.id, "must-not-exist", require_ready=True)
    with pytest.raises(StorageError, match="production creative"):
        service.review(
            preparation.id,
            kind="creative",
            expected_hash=job.output.sha256,
            expected_revision=0,
            reviewer="Fixture only",
            note="Must refuse",
        )
    with pytest.raises(StorageError, match="stale"):
        service.review(
            preparation.id,
            kind="metadata",
            expected_hash="0" * 64,
            expected_revision=0,
            reviewer="Fixture only",
            note="Must refuse",
        )
    reviewed = service.review(
        preparation.id,
        kind="metadata",
        expected_hash=inspection.metadata_sha256,
        expected_revision=0,
        reviewer="Fixture test",
        note="Public fixture text only",
    )
    assert (
        "metadata_and_disclosure_review_pending_or_stale" not in service.inspect(reviewed).blockers
    )
    with pytest.raises(RevisionConflict):
        service.save(preparation, expected_revision=0)
    changed = service.save(
        ReleasePreparation.model_validate({**reviewed.model_dump(), "description": "Edited text"}),
        expected_revision=reviewed.revision,
    )
    assert "metadata_and_disclosure_review_pending_or_stale" in service.inspect(changed).blockers
    source_hashes = {path: digest_file(jobs.assets.resolve(path.location)) for path in asset.files}
    report = service.export(preparation.id, "review-draft")
    root = jobs.store.root / report.bundle_path
    assert digest_file(root / "public/video.mp4") == (job.output.sha256, job.output.size_bytes)
    assert (root / "public/video.mp4").stat().st_ino != (
        jobs.store.root / job.destination
    ).stat().st_ino
    assert not (root / "public/chapters.txt").exists()
    public_text = "".join(
        path.read_text() for path in (root / "public").iterdir() if path.suffix != ".mp4"
    )
    assert secret not in public_text and str(jobs.store.root) not in public_text
    assert "source_project" not in public_text and "licence_evidence" not in public_text
    assert secret in (root / "private/music/music-test.json").read_text()
    for item in report.files:
        assert digest_file(jobs.store.root / item.location.path) == (item.sha256, item.size_bytes)
    assert (
        json.loads((root / "manifest.json").read_text())["inspection"]["status"]
        != "ready_for_manual_upload"
    )
    for item, digest_size in source_hashes.items():
        assert digest_file(jobs.assets.resolve(item.location)) == digest_size
    with pytest.raises(StorageError, match="exists"):
        service.export(preparation.id, "review-draft")
    with pytest.raises(ValueError):
        service.export(preparation.id, "../escape")
    # Publication is all-or-nothing if the preparation changes while copying.
    import tabi.core.publishing as publishing

    original = publishing.copy_verified

    def edit_during_copy(*args):
        original(*args)
        current = service.load(preparation.id)
        service.save(
            ReleasePreparation.model_validate(
                {**current.model_dump(), "title": "Changed concurrently"}
            ),
            expected_revision=current.revision,
        )

    monkeypatch.setattr(publishing, "copy_verified", edit_during_copy)
    with pytest.raises(StorageError, match="changed"):
        service.export(preparation.id, "race-rejected")
    assert not (root.parent / "race-rejected").exists()
    assert not list(root.parent.glob(".tabi-release-*"))
    # A matching title or saved review never conceals changed media bytes.
    (jobs.store.root / job.destination).write_bytes(b"changed output")
    with pytest.raises(ValueError, match="bytes differ"):
        service.export(preparation.id, "tamper-rejected")
    assert not (root.parent / "tamper-rejected").exists()
    assert digest_file(root / "public/video.mp4")[0] == job.output.sha256
