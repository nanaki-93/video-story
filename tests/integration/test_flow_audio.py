import json
import wave

import numpy as np
import pytest
from test_flow_assembly import ready_video

from tabi.core.assets import AssetService
from tabi.core.audio.mix import AudioMixer
from tabi.core.audio.pcm import PCMReader
from tabi.core.flow.assembly import FlowAssembler
from tabi.core.models.base import AssetRef, MediaPath
from tabi.core.models.episode import TrackPlacement
from tabi.core.models.registry import ImportRequest

pytestmark = pytest.mark.media


def test_continuous_soundtrack_exact_samples_and_original_preservation(tmp_path):
    settings, sources, service, episode = ready_video(tmp_path, counts=(24, 24))
    source = sources / "Music 東京.wav"
    pcm = (np.sin(np.arange(144000) * 2 * np.pi * 440 / 48000) * 4000).astype("<i2")
    with wave.open(str(source), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(48000)
        output.writeframes(pcm.tobytes())
    original = source.read_bytes()
    assets = AssetService(
        service.store, roots=service.media_roots, ffmpeg=settings.ffmpeg, ffprobe=settings.ffprobe
    )
    asset = assets.import_asset(
        ImportRequest(
            id="test.music",
            version="1.0",
            kind="audio",
            paths=[MediaPath(root_id="source", path=source.name)],
            provenance={"origin": "synthetic"},
        )
    )
    track = TrackPlacement(
        id="music",
        asset=AssetRef(id=asset.id, version=asset.version),
        start_sample=0,
        trim_start_sample=24000,
        trim_end_sample=120000,
    )
    assembler = FlowAssembler(service, settings)
    export = assembler.freeze(episode.id, revision=episode.revision, tracks=[track])
    pcm_path = tmp_path / "continuous.wav"
    mix = AudioMixer(assets, settings).render_tracks(
        export.inputs.tracks, export.inputs.audio_locks, 96000, export.inputs_sha256, pcm_path
    )
    with PCMReader(pcm_path) as reader:
        samples = np.concatenate([reader.read(0, 48000), reader.read(48000, 48000)])
    np.testing.assert_array_equal(samples[:, 0], (pcm[24000:120000] / 32768).astype("<f4"))
    np.testing.assert_array_equal(samples[:, 0], samples[:, 1])
    assert mix.sample_count == 96000 and mix.over_full_scale_samples == 0
    export = assembler.run(export.id)
    report = json.loads(service.store._read_bytes(export.report_path))
    assert report["audio"]["verification"]["intended_samples"] == 96000
    assert source.read_bytes() == original
    assert report["video"]["frame_count"] == 48
    another = assembler.freeze(episode.id, revision=episode.revision, tracks=[track])
    assets.resolve(asset.files[0].location).write_bytes(b"changed soundtrack copy")
    with pytest.raises(ValueError, match="changed"):
        assembler.run(another.id)
    assert service.get_export(another.id).state == "failed"
    assert not (service.store.root / f"exports/{another.id}.mp4").exists()
    assert source.read_bytes() == original


def test_silent_mode_stays_available(tmp_path):
    settings, _, service, episode = ready_video(tmp_path, counts=(24,))
    assembler = FlowAssembler(service, settings)
    silent = assembler.run(assembler.freeze(episode.id, revision=episode.revision).id)
    assert silent.inputs.profile.audio_codec is None
    assert json.loads(service.store._read_bytes(silent.report_path))["audio"] is None
