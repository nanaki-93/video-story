import csv
import io
from datetime import UTC, datetime

import pytest

from tabi.core.models.base import AssetRef, Canvas, FrameRate, content_hash
from tabi.core.models.production import ReviewRecord
from tabi.core.models.publishing import Chapter, PublicRelease, PublicTrack
from tabi.core.publishing import chapter_lines, review_status, tracklist_csv


def test_chapters_enforce_first_order_last_duration_and_no_rounded_markers():
    fps = FrameRate(num=30, den=1)
    chapters = [Chapter(start_frame=n, title=f"Part {i}") for i, n in enumerate((0, 300, 600))]
    assert chapter_lines(chapters, fps, 900) == (
        ["00:00 Part 0", "00:10 Part 1", "00:20 Part 2"],
        None,
    )
    for markers, duration in (
        (chapters[:2], 900),
        (chapters[1:], 900),
        (chapters[::-1], 900),
        (chapters, 899),
        ([chapters[0], Chapter(start_frame=301, title="Fraction"), chapters[2]], 900),
        ([chapters[0], Chapter(start_frame=300, title="Bad\nmarker"), chapters[2]], 900),
    ):
        lines, warning = chapter_lines(markers, fps, duration)
        assert not lines and "omitted" in warning
    # Exact integer-frame authoring at rational fps is not silently rounded.
    assert chapter_lines(chapters, FrameRate(num=30000, den=1001), 900)[1]
    assert chapter_lines([], fps, 900) == ([], None)


def test_csv_keeps_unknown_ids_blank_and_prevents_formula_execution():
    track = PublicTrack(
        placement_id="music",
        asset=AssetRef(id="track", version="1.0"),
        source_sha256="a" * 64,
        start_sample=17,
        end_sample=500,
        title='=1+1, "Tokyo"',
        artist="\t@private",
    )
    rows = list(csv.DictReader(io.StringIO(tracklist_csv([track]))))
    assert rows[0]["title"] == '\'=1+1, "Tokyo"'
    assert rows[0]["artist"] == "'\t@private"
    assert rows[0]["isrc"] == rows[0]["release_url"] == ""
    assert rows[0]["start_sample"] == "17"


def test_review_state_is_bound_to_export_and_all_public_metadata():
    public = PublicRelease(
        schema_version="1.0",
        title="Unit test only",
        description="",
        disclosure_notes="",
        purpose="production",
        video_sha256="a" * 64,
        snapshot_sha256="b" * 64,
        first_frame=0,
        frame_count=900,
        fps=FrameRate(num=30, den=1),
        canvas=Canvas(width=1920, height=1080),
        tracks=[],
        chapters=[],
        chapter_status="not_requested",
        thumbnail_sha256=None,
        rights=[],
    )

    def reviewed(digest):
        return ReviewRecord(
            reviewer="Unit fixture", reviewed_at=datetime.now(UTC), content_sha256=digest
        )

    creative, metadata = reviewed(public.video_sha256), reviewed(content_hash(public))
    assert review_status(public, [], None, None)[0] == "technically_verified"
    assert review_status(public, [], creative, None)[0] == "rights_reviewed"
    assert review_status(public, [], creative, metadata) == ("ready_for_manual_upload", [])
    for blocker in ("partial_export", "synthetic_assets", "music_rights_pending"):
        assert review_status(public, [blocker], creative, metadata) == (
            "creatively_reviewed",
            [blocker],
        )
    for field, value in (
        ("description", "Edited"),
        ("disclosure_notes", "Edited"),
        ("video_sha256", "c" * 64),
    ):
        changed = PublicRelease.model_validate({**public.model_dump(), field: value})
        status, blockers = review_status(changed, [], creative, metadata)
        assert status != "ready_for_manual_upload"
        assert "metadata_and_disclosure_review_pending_or_stale" in blockers
        if field == "video_sha256":
            assert "creative_review_pending_or_stale" in blockers
    with pytest.raises(ValueError):
        PublicRelease.model_validate({**public.model_dump(), "private_licence": "secret"})
