import json

import numpy as np
import pytest
from test_flow_import import accept_last, make_clip, media_context, pending

from tabi.core.flow.assembly import FlowAssembler
from tabi.core.flow.media import FlowMedia
from tabi.core.flow.service import FlowError, updated
from tabi.core.models.base import FrameRate, MediaPath
from tabi.core.process import run_tool
from tabi.core.render.ffmpeg import verify_video

pytestmark = pytest.mark.media


def ready_video(tmp_path, counts=(192, 168, 168), target=None):
    settings, sources, service, episode = media_context(tmp_path, target=target or sum(counts))
    for index, frames in enumerate(counts):
        path = sources / f"clip {index} 東京.mp4"
        make_clip(settings, path, frames=frames, hue=index * 40)
        episode = pending(service, episode)
        episode = FlowMedia(service, settings).import_result(
            episode.id,
            episode.attempts[-1].id,
            MediaPath(root_id="source", path=path.name),
            revision=episode.revision,
            synthetic=True,
        )
        episode = accept_last(service, episode)
    return settings, sources, service, episode


def test_8_7_7_assembly_has_exact_frames_and_continuous_pts(tmp_path):
    settings, sources, service, episode = ready_video(tmp_path)
    originals = [path.read_bytes() for path in sorted(sources.glob("*.mp4"))]
    assembler = FlowAssembler(service, settings)
    export = assembler.freeze(episode.id, revision=episode.revision)
    # Later draft changes do not change frozen export inputs.
    service.save(updated(episode, title="Next edit"), expected_revision=episode.revision)
    export = assembler.run(export.id)
    assert export.state == "verified"
    video = verify_video(settings, service.verify_file(export.output), export.inputs.profile, 528)
    assert video.frame_count == 528 and video.duration_seconds == 22
    report = json.loads(service.store._read_bytes(export.report_path))
    assert report["synthetic"] and report["creative_approval"] == "pending"
    output_path = service.verify_file(export.output)
    for global_frame, source_index, local_frame in [
        (191, 0, 191),
        (192, 1, 0),
        (359, 1, 167),
        (360, 2, 0),
    ]:

        def rgb(path, frame):
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

        source_path = service.verify_file(episode.candidates[source_index].media)
        assert np.mean(np.abs(rgb(output_path, global_frame) - rgb(source_path, local_frame))) < 4
    assert [path.read_bytes() for path in sorted(sources.glob("*.mp4"))] == originals
    assert assembler.run(export.id) == export
    # A crash after publication is reconciled from the verified report and file.
    service.save_export(
        updated(export, state="interrupted", output=None), expected_revision=export.revision
    )
    assert assembler.run(export.id).state == "verified"


def test_reviewed_safe_cut_is_exact_and_source_change_fails_atomically(tmp_path):
    settings, _, service, episode = ready_video(tmp_path, counts=(48,), target=36)
    candidate = updated(episode.candidates[0], safe_end_frame=36)
    episode = service.save(
        updated(episode, candidates=[candidate]), expected_revision=episode.revision
    )
    assembler = FlowAssembler(service, settings)
    export = assembler.freeze(episode.id, revision=episode.revision)
    export = assembler.run(export.id)
    assert (
        verify_video(
            settings, service.verify_file(export.output), export.inputs.profile, 36
        ).frame_count
        == 36
    )
    another = assembler.freeze(episode.id, revision=episode.revision)
    service.verify_file(candidate.media).write_bytes(b"changed")
    with pytest.raises(FlowError, match="changed"):
        assembler.run(another.id)
    assert service.get_export(another.id).state == "failed"
    assert not (service.store.root / f"exports/{another.id}.mp4").exists()


def test_fractional_native_rate_is_preserved(tmp_path):
    settings, sources, service, episode = media_context(tmp_path, target=60)
    fps = FrameRate(num=30000, den=1001)
    episode = service.save(
        updated(episode, recipe=updated(episode.recipe, fps=fps)),
        expected_revision=episode.revision,
    )
    for index in range(2):
        path = sources / f"fractional-{index}.mp4"
        run_tool(
            [
                settings.ffmpeg,
                "-v",
                "error",
                "-nostdin",
                "-f",
                "lavfi",
                "-i",
                "testsrc2=size=96x54:rate=30000/1001",
                "-frames:v",
                "30",
                "-vf",
                f"hue=h={index * 40}",
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
        episode = accept_last(service, episode)
    assembler = FlowAssembler(service, settings)
    export = assembler.run(assembler.freeze(episode.id, revision=episode.revision).id)
    video = verify_video(settings, service.verify_file(export.output), export.inputs.profile, 60)
    assert video.fps == fps and abs(video.duration_seconds - 2.002) < 0.0001
