import hashlib
import json
import math
import struct
import wave
from fractions import Fraction

import numpy as np
import pytest

from tabi.cli.main import main
from tabi.core.assets import AssetService
from tabi.core.audio import AudioService
from tabi.core.audio.pcm import PCMReader, decode_pcm, placement_block
from tabi.core.audio.timeline import prepared_samples
from tabi.core.fixtures import generate_fixtures
from tabi.core.models import Episode, ReleaseRecord, TrackPlacement
from tabi.core.models.base import AssetRef, MediaPath
from tabi.core.models.registry import ImportRequest
from tabi.core.persistence import ProjectStore, StorageError


@pytest.fixture
def audio(tmp_path):
    root = tmp_path / "音楽's project"
    generate_fixtures(root)
    store = ProjectStore(root)
    return AudioService(AssetService(store)), store.read("episodes/episode.synthetic.json")


def write_pcm(path, values, width=2, channels=1, rate=48000):
    with wave.open(str(path), "wb") as stream:
        stream.setnchannels(channels)
        stream.setsampwidth(width)
        stream.setframerate(rate)
        stream.writeframes(
            b"".join(int(n).to_bytes(width, "little", signed=width != 1) for n in values)
        )


def test_pcm_widths_signedness_channels_and_truncation():
    for width in [1, 2, 3, 4]:
        scale = 2 ** (8 * width - 1)
        samples = [-scale, -1, 0, 1, scale - 1, scale // 2]
        encoded = b"".join(
            (n + (128 if width == 1 else 0)).to_bytes(width, "little", signed=width != 1)
            for n in samples
        )
        np.testing.assert_array_equal(
            decode_pcm(encoded, width, 2).ravel(), np.array(samples) / scale
        )
    with pytest.raises(ValueError, match="truncated"):
        decode_pcm(b"\x00", 3, 2)


def test_reference_trim_fades_gain_and_global_ranges(tmp_path):
    path = tmp_path / "master 東京.wav"
    values = [12000] * 20
    write_pcm(path, values)
    placement = TrackPlacement(
        id="test",
        asset=AssetRef(id="source", version="1.0"),
        start_sample=4,
        trim_start_sample=3,
        trim_end_sample=15,
        fade_in_samples=4,
        fade_out_samples=5,
        gain_db=-6,
    )
    reference = []
    for n in range(24):
        offset = n - 4
        if 0 <= offset < 12:
            gain = min(1, offset / 3) * min(1, (11 - offset) / 4) * math.pow(10, -6 / 20)
            reference.append([12000 / 32768 * gain] * 2)
        else:
            reference.append([0, 0])
    before = path.read_bytes()
    with PCMReader(path) as reader:
        all_samples = placement_block(reader, placement, 0, 24)
        np.testing.assert_allclose(all_samples, reference, rtol=0, atol=1e-15)
        for boundary in range(25):
            split = np.concatenate(
                [
                    placement_block(reader, placement, 0, boundary),
                    placement_block(reader, placement, boundary, 24 - boundary),
                ]
            )
            np.testing.assert_array_equal(split, all_samples)
    assert path.read_bytes() == before
    assert np.all(all_samples[4] == 0) and np.all(all_samples[15] == 0)
    assert all_samples[7, 0] == pytest.approx(12000 / 32768 * 10 ** (-6 / 20))


def test_trim_uses_distinct_source_samples_and_single_sample_fades(tmp_path):
    path = tmp_path / "distinct.wav"
    write_pcm(path, list(range(100, 112)))
    placement = TrackPlacement(
        id="test",
        asset=AssetRef(id="source", version="1.0"),
        start_sample=3,
        trim_start_sample=2,
        trim_end_sample=9,
        fade_in_samples=1,
        fade_out_samples=1,
    )
    with PCMReader(path) as reader:
        samples = placement_block(reader, placement, 2, 9)
        np.testing.assert_array_equal(
            samples[:, 0], np.array([0, 0, 103, 104, 105, 106, 107, 0, 0]) / 32768
        )
        with pytest.raises(ValueError, match="sufficient"):
            placement_block(reader, placement.model_copy(update={"trim_end_sample": 13}), 0, 5)


def test_waveform_matches_independent_bins_and_original_master(audio):
    service, _ = audio
    ref = AssetRef(id="fixture.tone", version="1.0")
    asset = service.assets.load(ref)
    path = service.assets.resolve(asset.files[0].location)
    before = hashlib.sha256(path.read_bytes()).hexdigest()
    result = service.waveform(ref, bins=13)
    with wave.open(str(path)) as stream:
        data = stream.readframes(stream.getnframes())
    values = struct.unpack(f"<{len(data) // 2}h", data)
    for item in result.bins:
        for channel in range(2):
            samples = values[item.start_sample * 2 + channel : item.end_sample * 2 : 2]
            assert item.minimum[channel] == min(samples) / 32768
            assert item.maximum[channel] == max(samples) / 32768
            assert item.rms[channel] == pytest.approx(
                math.sqrt(sum(n * n for n in samples) / len(samples)) / 32768
            )
    assert result.synthetic and not result.silent
    assert hashlib.sha256(path.read_bytes()).hexdigest() == before == result.source_sha256
    silence = service.waveform(AssetRef(id="fixture.silence", version="1.0"), bins=7)
    assert silence.silent and silence.leading_silence_samples == silence.duration_samples
    assert silence.trailing_silence_samples == silence.duration_samples
    assert all(item.rms == [0, 0] for item in silence.bins)
    with pytest.raises(ValueError, match="bins"):
        service.waveform(ref, bins=8193)


def test_timeline_order_overlaps_gaps_invalid_trims_and_source_rate(audio):
    service, episode = audio
    track = episode.tracks[0]
    track = track.model_copy(update={"fade_in_samples": 0, "fade_out_samples": 0})
    data = episode.model_dump()
    data["tracks"] = [
        {**track.model_dump(), "id": "later", "start_sample": 200, "trim_end_sample": 200},
        {**track.model_dump(), "id": "earlier", "start_sample": 50, "trim_end_sample": 200},
    ]
    report = service.inspect(Episode.model_validate(data))
    assert [p.id for p in report.placements] == ["earlier", "later"]
    assert [(g.start_sample, g.end_sample) for g in report.music_gaps] == [(0, 50), (400, 480000)]
    assert {i.code for i in report.issues} == {"music_gap", "music_overlap"}
    silent = Episode.model_validate(
        {
            **episode.model_dump(),
            "tracks": [
                {
                    **track.model_dump(),
                    "asset": {"id": "fixture.silence", "version": "1.0"},
                    "trim_end_sample": 48000,
                }
            ],
        }
    )
    assert "silent_master" in {i.code for i in service.inspect(silent).issues}
    data["tracks"][0].update(start_sample=0, trim_start_sample=500000, trim_end_sample=500200)
    with pytest.raises(ValueError, match="trim exceeds"):
        service.inspect(Episode.model_validate(data))
    source = service.assets.load(track.asset)
    changed = source.model_copy(
        update={"probe": source.probe.model_copy(update={"sample_rate": 44100})}
    )
    assert prepared_samples(changed) == round(Fraction(480000 * 48000, 44100))


def test_import_wav_release_metadata_and_cli_preserve_master(audio, tmp_path, capsys):
    service, _ = audio
    source = tmp_path / "Master's 音.wav"
    write_pcm(source, [0, 1, -1, 200, -200, 0], width=3, rate=44100)
    original = source.read_bytes()
    service.assets.roots["music"] = tmp_path
    asset = service.assets.import_asset(
        ImportRequest(
            id="original",
            version="1.0",
            kind="audio",
            paths=[MediaPath(root_id="music", path=source.name)],
        )
    )
    assert service.assets.resolve(asset.files[0].location).read_bytes() == original
    record = ReleaseRecord.model_validate(
        {
            "schema_version": "1.0",
            "document_type": "release_record",
            "id": "release.test",
            "artist": "Synthetic test",
            "release_title": "Metadata test only",
            "tracks": [
                {
                    "asset": {"id": asset.id, "version": asset.version},
                    "title": "Test",
                    "master": asset.source.model_dump(),
                    "sample_rate": 44100,
                    "duration_samples": 6,
                    "channels": 1,
                    "credits": [{"name": "Test", "role": "fixture"}],
                }
            ],
        }
    )
    bad = record.model_copy(
        update={"tracks": [record.tracks[0].model_copy(update={"sha256": "a" * 64})]}
    )
    with pytest.raises(ValueError, match="hash"):
        service.import_release(bad)
    saved = service.import_release(record)
    assert saved.tracks[0].sha256 == hashlib.sha256(original).hexdigest()
    assert saved.tracks[0].isrc is None and saved.upc is None and saved.rights_status == "pending"
    assert saved.tracks[0].master == asset.files[0].location
    assert source.read_bytes() == original
    output = tmp_path / "waveform.json"
    args = [
        "audio",
        "waveform",
        "original",
        "1.0",
        "--project",
        str(service.store.root),
        "--output",
        str(output),
    ]
    assert main(args) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["duration_samples"] == 6 and report["bins"][1]["start_sample"] == 1
    assert main(args) == 4
    assert "exists" in capsys.readouterr().err
    with pytest.raises(StorageError):
        service.import_release(record)
