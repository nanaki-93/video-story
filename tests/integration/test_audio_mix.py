import hashlib
import math
import os
import wave
from pathlib import Path

import numpy as np
import pytest

from tabi.core.assets import AssetService
from tabi.core.audio.mix import AudioMixer
from tabi.core.audio.pcm import BLOCK_SAMPLES, PCMReader, placement_block
from tabi.core.config import load_settings
from tabi.core.episodes import EpisodeService
from tabi.core.fixtures import generate_fixtures
from tabi.core.models import Episode
from tabi.core.models.base import AssetRef, Canvas, MediaPath
from tabi.core.models.registry import ImportRequest
from tabi.core.persistence import ProjectStore
from tabi.core.process import run_tool
from tabi.core.timeline.compiler import ActionCompiler

pytestmark = pytest.mark.media


@pytest.fixture
def setup(tmp_path):
    root = tmp_path / "Sound's 東京 project"
    generate_fixtures(root)
    store = ProjectStore(root)
    settings = load_settings(None, env=os.environ, cwd=Path.cwd(), home=Path.home())
    assets = AssetService(store, ffmpeg=settings.ffmpeg, ffprobe=settings.ffprobe)
    return assets, settings, store.read("episodes/episode.synthetic.json")


def read_all(path):
    with PCMReader(path) as reader:
        return np.concatenate(
            [
                reader.read(start, min(BLOCK_SAMPLES, reader.samples - start))
                for start in range(0, reader.samples, BLOCK_SAMPLES)
            ]
        )


def test_continuous_mix_and_arbitrary_range_match_reference_samples(setup, tmp_path):
    assets, settings, episode = setup
    source = assets.resolve(assets.load(episode.tracks[0].asset).files[0].location)
    before = source.read_bytes()
    snapshot = ActionCompiler(assets, purpose="synthetic_test").compile(episode)
    mixer = AudioMixer(assets, settings)
    output = tmp_path / "continuous.wav"
    report = mixer.render(snapshot, output)
    full = read_all(output)
    with wave.open(str(source), "rb") as original:
        pcm = np.frombuffer(original.readframes(480000), dtype="<i2").reshape(-1, 2) / 32768
    envelope = np.ones(480000)
    envelope[:480] = np.arange(480) / 479
    envelope[-480:] = np.arange(479, -1, -1) / 479
    np.testing.assert_array_equal(full, (pcm * envelope[:, None]).astype("<f4"))
    part = tmp_path / "part.wav"
    mixer.render(snapshot, part, start_sample=65530, end_sample=144017)
    np.testing.assert_array_equal(read_all(part), full[65530:144017])
    assert report.verified_samples and report.sample_count == 480000
    assert report.over_full_scale_samples == 0 and report.integrated_lufs is not None
    assert report.sample_peak_dbfs == pytest.approx(20 * math.log10(3840 / 32768))
    assert source.read_bytes() == before
    with pytest.raises(ValueError, match="new WAV"):
        mixer.render(snapshot, output)


def test_resampling_float_master_keeps_count_frequency_and_original_hash(setup, tmp_path):
    assets, settings, episode = setup
    source = assets.store.root / "master44100.wav"
    # Ask the actual media tool to generate an extensible IEEE-float WAV, not a mocked probe.
    run_tool(
        [
            settings.ffmpeg,
            "-v",
            "error",
            "-nostdin",
            "-n",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=997:sample_rate=44100:duration=1",
            "-c:a",
            "pcm_f64le",
            "-rf64",
            "always",
            str(source),
        ]
    )
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    asset = assets.import_asset(
        ImportRequest(
            id="test.float",
            version="1.0",
            kind="audio",
            paths=[MediaPath(path=source.name)],
            provenance={"origin": "synthetic"},
        )
    )
    data = episode.model_dump()
    data["tracks"] = [
        {
            **episode.tracks[0].model_dump(),
            "asset": {"id": asset.id, "version": asset.version},
            "trim_end_sample": 48000,
            "fade_in_samples": 0,
            "fade_out_samples": 0,
        }
    ]
    snapshot = ActionCompiler(assets, purpose="synthetic_test").compile(
        Episode.model_validate(data)
    )
    output = tmp_path / "resampled.wav"
    report = AudioMixer(assets, settings).render(snapshot, output, end_sample=48000)
    samples = read_all(output)
    assert samples.shape == (48000, 2) and report.preparations[0].resampled
    spectrum = np.abs(np.fft.rfft(samples[:, 0]))
    assert np.argmax(spectrum) == 997
    np.testing.assert_array_equal(samples[:, 0], samples[:, 1])
    assert hashlib.sha256(source.read_bytes()).hexdigest() == before


def test_ambience_continuity_and_explicit_overload_report(setup, tmp_path):
    assets, settings, episode = setup
    track = episode.tracks[0].model_dump()
    ambience = {
        **track,
        "id": "ambience",
        "role": "ambience",
        "trim_end_sample": 4800,
        "loop_duration_samples": 480000,
        "loop_crossfade_samples": 96,
        "gain_db": -12.0,
    }
    snapshot = ActionCompiler(assets, purpose="synthetic_test").compile(
        Episode.model_validate(
            {
                **episode.model_dump(),
                "tracks": [ambience],
            }
        )
    )
    output = tmp_path / "ambience.wav"
    AudioMixer(assets, settings).render(snapshot, output)
    samples = read_all(output)
    source = read_all(assets.resolve(assets.load(episode.tracks[0].asset).files[0].location))[
        :4800, 0
    ]
    gain = 10 ** (-12 / 20)
    ordinary_step = np.max(np.abs(np.diff(source))) * gain
    overlap_step = np.max(np.abs(source[4704:] - source[:96])) * gain / 95
    endpoint_fade_step = np.max(np.abs(source)) * gain / 479
    assert (
        np.max(np.abs(np.diff(samples[:, 0])))
        <= ordinary_step + overlap_step + endpoint_fade_step + 1e-8
    )
    for boundary in range(4704, 480000 - 480, 4704):
        assert abs(samples[boundary, 0] - samples[boundary - 1, 0]) <= ordinary_step + 1e-8
    peak_snapshot = ActionCompiler(assets, purpose="synthetic_test").compile(
        Episode.model_validate(
            {
                **episode.model_dump(),
                "tracks": [{**track, "gain_db": 24.0}],
            }
        )
    )
    overloaded = tmp_path / "float-overload.wav"
    report = AudioMixer(assets, settings).render(peak_snapshot, overloaded)
    assert report.over_full_scale_samples > 0 and report.suggested_gain_db < 0
    assert np.max(np.abs(read_all(overloaded))) > 1  # Float data preserved; no hidden limiter.
    digest = assets.store.save_snapshot(peak_snapshot)
    service = EpisodeService(assets, settings)
    blocked = tmp_path / "clipped.mp4"
    with pytest.raises(ValueError, match="exceeds full scale"):
        service.preview(digest, 30, 31, blocked, canvas=Canvas(width=640, height=360))
    assert not blocked.exists()
    adjusted = service.preview(
        digest,
        30,
        31,
        tmp_path / "adjusted.mp4",
        canvas=Canvas(width=640, height=360),
        audio_gain_db=-6.0,
    )
    assert adjusted.audio_mix.gain_db == -6.0 and adjusted.audio_mix.over_full_scale_samples == 0


def test_preview_aac_has_global_sample_phase_and_single_encode(setup, tmp_path, monkeypatch):
    from tabi.core.audio import mix

    calls = []

    def observed(args, **kwargs):
        calls.append(args)
        return run_tool(args, **kwargs)

    monkeypatch.setattr(mix, "run_tool", observed)
    assets, settings, episode = setup
    service = EpisodeService(assets, settings)
    compiled = service.compile(episode, purpose="synthetic_test")
    output = tmp_path / "audio-preview.mp4"
    report = service.preview(
        compiled.snapshot_sha256, 149, 181, output, canvas=Canvas(width=640, height=360)
    )
    assert report.audio_mix.first_sample == 149 * 1600
    assert report.audio_mix.sample_count == report.audio_verification.intended_samples == 32 * 1600
    decoded = tmp_path / "decoded.f32"
    run_tool(
        [
            settings.ffmpeg,
            "-v",
            "error",
            "-nostdin",
            "-n",
            "-i",
            str(output),
            "-map",
            "0:a:0",
            "-f",
            "f32le",
            str(decoded),
        ]
    )
    actual = np.fromfile(decoded, dtype="<f4").reshape(-1, 2)[: 32 * 1600]
    path = assets.resolve(assets.load(AssetRef(id="fixture.tone", version="1.0")).files[0].location)
    with PCMReader(path) as reader:
        reference = placement_block(reader, episode.tracks[0], 149 * 1600, 32 * 1600)
    assert np.corrcoef(actual[1024:-1024, 0], reference[1024:-1024, 0])[0, 1] > 0.995
    assert np.sqrt(np.mean((actual[1024:-1024] - reference[1024:-1024]) ** 2)) < 0.003
    assert report.audio_mix.output is None  # No stale temporary path presented as a saved artifact.
    assert sum("-c:a" in args and args[args.index("-c:a") + 1] == "aac" for args in calls) == 1


def test_silent_mix_and_failed_verification_never_publish(setup, tmp_path, monkeypatch):
    assets, settings, episode = setup
    snapshot = ActionCompiler(assets, purpose="synthetic_test").compile(
        episode.model_copy(update={"tracks": []})
    )
    output = tmp_path / "silence.wav"
    report = AudioMixer(assets, settings).render(snapshot, output, end_sample=48000)
    assert report.integrated_lufs is None and report.sample_peak_dbfs is None and report.warnings
    assert np.max(np.abs(read_all(output))) == 0
    from tabi.core.audio import mix

    monkeypatch.setattr(
        mix,
        "measure_loudness",
        lambda *_: (_ for _ in ()).throw(ValueError("injected verification failure")),
    )
    failed = tmp_path / "no.wav"
    with pytest.raises(ValueError, match="injected"):
        AudioMixer(assets, settings).render(snapshot, failed, end_sample=48000)
    assert not failed.exists()
    assert not list(tmp_path.glob(".tabi-audio-*"))
