import pytest
from test_flow_import import accept_last, make_clip, media_context, pending

from tabi.core.flow.media import FlowMedia
from tabi.core.flow.review import FlowReview
from tabi.core.flow.service import FlowError
from tabi.core.models.base import HashedFile, MediaPath
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
