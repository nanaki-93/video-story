import pytest
from test_flow_import import accept_last, make_clip, media_context, pending

from tabi.core.assets.probe import probe_media
from tabi.core.flow.media import FlowMedia
from tabi.core.flow.review import FlowReview
from tabi.core.flow.service import FlowError
from tabi.core.models.base import FrameInterval, HashedFile, MediaPath
from tabi.core.process import run_tool

pytestmark = pytest.mark.media


def test_native_review_samples_and_join_playback_bind_exact_hashes(tmp_path):
    settings, sources, service, episode = media_context(tmp_path)
    importer, review = FlowMedia(service, settings), FlowReview(service, settings)
    for index in range(2):
        path = sources / f"clip{index}.mp4"
        make_clip(settings, path, frames=48, hue=index * 20)
        episode = pending(service, episode)
        episode = importer.import_result(
            episode.id,
            episode.attempts[-1].id,
            MediaPath(root_id="source", path=path.name),
            revision=episode.revision,
            synthetic=True,
        )
        episode = review.prepare(episode.id, episode.candidates[-1].id, revision=episode.revision)
        packet = review.read(episode.candidates[-1])
        assert packet["candidate_sha256"] == episode.candidates[-1].media.sha256
        assert packet["diagnostics"]["advisory_only"]
        assert "unassessed" in packet["diagnostics"]["window_motion"]
        assert len(packet["images"]) == 5 + index
        for image in packet["images"]:
            assert service.verify_file(HashedFile.model_validate(image["media"])).is_file()
        if index:
            assert service.verify_file(HashedFile.model_validate(packet["join_video"])).is_file()
        episode = accept_last(service, episode)
    media = episode.candidates[-1].media
    service.verify_file(media).write_bytes(b"changed")
    with pytest.raises(FlowError, match="changed"):
        review.prepare(episode.id, episode.candidates[-1].id, revision=episode.revision)


def test_stillness_is_reported_but_not_automatically_rejected(tmp_path):
    settings, sources, service, episode = media_context(tmp_path)
    path = sources / "still.mp4"
    run_tool(
        [
            settings.ffmpeg,
            "-v",
            "error",
            "-nostdin",
            "-f",
            "lavfi",
            "-i",
            "color=c=blue:size=96x54:rate=24",
            "-frames:v",
            "48",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            str(path),
        ]
    )
    episode = pending(service, episode)
    episode = FlowMedia(service, settings).import_result(
        episode.id,
        episode.attempts[-1].id,
        MediaPath(root_id="source", path=path.name),
        revision=episode.revision,
        synthetic=True,
    )
    review = FlowReview(service, settings)
    episode = review.prepare(episode.id, episode.candidates[-1].id, revision=episode.revision)
    packet = review.read(episode.candidates[-1])
    assert packet["diagnostics"]["repeated_scaled_frames"] == [{"start_frame": 0, "end_frame": 48}]
    assert episode.candidates[-1].review == "pending" and episode.candidates[-1].technical_ok


def test_selected_section_is_atomic_range_bound_and_preserves_the_source(tmp_path, monkeypatch):
    settings, sources, service, episode = media_context(tmp_path, target=24)
    path = sources / "Tokyo original.mp4"
    make_clip(settings, path, frames=48)
    original = path.read_bytes()
    episode = pending(service, episode)
    episode = FlowMedia(service, settings).import_result(
        episode.id,
        episode.attempts[-1].id,
        MediaPath(root_id="source", path=path.name),
        revision=episode.revision,
        synthetic=True,
    )
    review = FlowReview(service, settings)
    candidate = episode.candidates[-1]
    episode = review.prepare(episode.id, candidate.id, revision=episode.revision)
    before = episode
    section = FrameInterval(start_frame=12, end_frame=36)

    def select(revision=None, digest=None):
        return review.prepare(
            episode.id,
            candidate.id,
            revision=episode.revision if revision is None else revision,
            trim=section,
            media_sha256=digest or candidate.media.sha256,
        )

    with pytest.raises(FlowError, match="changed"):
        select(revision=episode.revision - 1)
    with pytest.raises(FlowError, match="stale"):
        select(digest="0" * 64)
    with monkeypatch.context() as patch:
        patch.setattr(review, "_image", lambda *args: (_ for _ in ()).throw(RuntimeError("disk")))
        with pytest.raises(RuntimeError, match="disk"):
            select()
    assert service.get(episode.id) == before
    episode = select()
    selected = episode.candidates[-1]
    packet = review.read(selected)
    assert selected.trim == section and selected.review == "pending"
    assert packet["candidate_trim"] == section.model_dump()
    assert [i["frame"] for i in packet["images"]] == [12, 18, 24, 30, 35]
    preview = service.verify_file(HashedFile.model_validate(packet["selected_video"]))
    probe = probe_media(
        [preview], "video", fps=None, ffmpeg=settings.ffmpeg, ffprobe=settings.ffprobe
    )
    assert probe.frame_count == 24 and probe.fps == candidate.fps
    expected, actual = review._frames(path, 12, 36), review._frames(preview, 0, 24)
    assert all(
        sum(abs(x - y) for x, y in zip(a, b, strict=True)) / len(a) < 3
        for a, b in zip(expected, actual, strict=True)
    )
    assert path.read_bytes() == original
    assert service.verify_file(candidate.media).read_bytes() == original
    assert before.candidates[-1].trim == FrameInterval(start_frame=0, end_frame=48)
    episode = accept_last(service, episode)
    with pytest.raises(FlowError, match="already been reviewed"):
        select()
