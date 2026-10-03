import os
from pathlib import Path

import pytest

from tabi.core.config import load_settings
from tabi.core.episodes import EpisodeService
from tabi.core.jobs import JobService
from tabi.core.models.base import AssetRef
from tabi.core.models.production import OutputProfile
from tabi.core.render.backend import FrozenRegistry


@pytest.mark.media
def test_explicit_review_to_production_export_uses_frozen_approved_inputs(review_project, tmp_path):
    author, template, pack, episode = review_project
    review = {
        "reviewer": "Temporary automated test",
        "note": "Owned geometry exercises the approval policy only; no real artwork approval",
    }
    for asset in author.assets.list_assets():
        author.assets.approve(
            AssetRef(id=asset.id, version=asset.version),
            expected_hash=asset.approval_hash,
            **review,
        )
    for document in (template, pack):
        author.review_metadata(
            document.document_type,
            AssetRef(id=document.id, version=document.version),
            expected_hash=document.approval_hash,
            **review,
        )
    settings = load_settings(None, env=os.environ, cwd=Path.cwd(), home=tmp_path)
    service = EpisodeService(author.assets, settings)
    compiled = service.compile(episode, purpose="production")
    reviewed = service.review_snapshot(
        compiled.snapshot_sha256, expected_hash=compiled.review_content_sha256, **review
    )
    assert compiled.snapshot_sha256 != reviewed.snapshot_sha256
    assert author.store.read_snapshot(compiled.snapshot_sha256).approval.status == "draft"
    frozen = author.store.read_snapshot(reviewed.snapshot_sha256)
    assert frozen.approval.status == "approved"
    registry = FrozenRegistry(author.assets, frozen)
    assert all(document.approval.status == "approved" for document in registry.documents.values())
    jobs = JobService(author.assets, settings)
    job = jobs.submit(
        reviewed.snapshot_sha256,
        OutputProfile(
            id="tiny-review-check",
            canvas=episode.canvas,
            fps=episode.fps,
            container="mp4",
            video_codec="libx264",
            pixel_format="yuv420p",
            color_space="bt709",
            audio_codec="aac",
        ),
        "exports/review.mp4",
        max_chunk_frames=11,
    )
    result = jobs.work(once=True)[0]
    assert result.state == "verified", result.error
    assert len(result.chunks) == 3
    report = jobs.verify_export(job.id)
    assert report.video.frame_count == 30 and report.audio.decoded_samples == 48000
