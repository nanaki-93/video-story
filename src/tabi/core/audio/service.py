"""Audio source analysis and factual release import over the shared asset registry."""

import numpy as np

from ..assets import AssetService
from ..assets.service import digest_file
from ..models import Episode, ReleaseRecord
from ..models.audio import AudioTimelineReport, WaveformBin, WaveformReport
from ..models.base import AssetRef
from ..models.production import ReleaseTrack, ValidationIssue
from .pcm import BLOCK_SAMPLES, PCMReader
from .timeline import inspect_timeline, prepared_samples


class AudioService:
    def __init__(self, assets: AssetService):
        self.assets, self.store = assets, assets.store

    def inspect(self, episode: Episode) -> AudioTimelineReport:
        report = inspect_timeline(episode, self.assets.require_valid)
        analyzed = set()
        issues = list(report.issues)
        for track in report.placements:
            if track.release_id is not None:
                release = self.store.read(f"releases/{track.release_id}.json")
                if not isinstance(release, ReleaseRecord) or not any(
                    item.asset == track.asset for item in release.tracks
                ):
                    raise ValueError(f"release metadata does not contain track {track.id}")
            key = (track.asset.id, track.asset.version)
            if key not in analyzed:
                waveform = self.waveform(track.asset, bins=1)
                if waveform.silent:
                    issues.append(
                        ValidationIssue(
                            severity="warning",
                            code="silent_master",
                            location=["tracks", track.id],
                            message="This source master contains only zero-valued PCM samples.",
                            suggested_fix=(
                                "Confirm intentional silence or import the finished master."
                            ),
                        )
                    )
                analyzed.add(key)
        return AudioTimelineReport.model_validate({**report.model_dump(), "issues": issues})

    def waveform(self, reference: AssetRef, *, bins: int = 512) -> WaveformReport:
        if type(bins) is not int or not 1 <= bins <= 8192:
            raise ValueError("waveform bins must be an integer from 1 to 8192")
        asset = self.assets.require_valid(reference)
        prepared_samples(asset)
        source = self.assets.resolve(asset.files[0].location)
        result = []
        first_nonzero, last_nonzero = None, None
        with PCMReader(source) as reader:
            if (reader.samples, reader.rate, reader.channels) != (
                asset.probe.duration_samples,
                asset.probe.sample_rate,
                asset.probe.channels,
            ):
                raise ValueError("WAV header differs from its registry metadata")
            bins = min(bins, reader.samples)
            for index in range(bins):
                first = index * reader.samples // bins
                end = (index + 1) * reader.samples // bins
                minimum = np.full(reader.channels, np.inf)
                maximum = np.full(reader.channels, -np.inf)
                squared = np.zeros(reader.channels)
                for start in range(first, end, BLOCK_SAMPLES):
                    samples = reader.read(start, min(BLOCK_SAMPLES, end - start))
                    minimum = np.minimum(minimum, samples.min(axis=0))
                    maximum = np.maximum(maximum, samples.max(axis=0))
                    squared += (samples * samples).sum(axis=0)
                    nonzero = np.flatnonzero(np.any(samples != 0, axis=1))
                    if nonzero.size:
                        if first_nonzero is None:
                            first_nonzero = start + int(nonzero[0])
                        last_nonzero = start + int(nonzero[-1])
                result.append(
                    WaveformBin(
                        start_sample=first,
                        end_sample=end,
                        minimum=minimum.tolist(),
                        maximum=maximum.tolist(),
                        rms=np.sqrt(squared / (end - first)).tolist(),
                    )
                )
        if self.assets.require_valid(reference) != asset:
            raise ValueError("asset changed while generating its waveform")
        return WaveformReport(
            schema_version="1.0",
            asset=reference,
            asset_content_sha256=asset.approval_hash,
            source_sha256=asset.files[0].sha256,
            sample_rate=reader.rate,
            duration_samples=reader.samples,
            channels=reader.channels,
            bins=result,
            leading_silence_samples=reader.samples if first_nonzero is None else first_nonzero,
            trailing_silence_samples=(
                reader.samples if last_nonzero is None else reader.samples - last_nonzero - 1
            ),
            silent=first_nonzero is None,
            synthetic=asset.provenance.origin == "synthetic",
        )

    def import_release(self, record: ReleaseRecord) -> ReleaseRecord:
        record = ReleaseRecord.model_validate(record)
        if record.status != "draft" or record.revision != 0:
            raise ValueError("import release metadata as a new draft; reviews are separate")
        return self.save_release(record, expected_revision=None)

    def save_release(self, record: ReleaseRecord, *, expected_revision) -> ReleaseRecord:
        record = ReleaseRecord.model_validate(record)
        if record.status != "draft" or record.creative_review is not None:
            raise ValueError("Music metadata editing accepts drafts without creative approval only")
        if expected_revision is not None:
            previous = self.store.read(f"releases/{record.id}.json")
            if previous.status != "draft":
                raise ValueError("Reviewed release metadata is preserved; create a new draft ID")
        tracks = []
        for track in record.tracks:
            asset = self.assets.require_valid(track.asset)
            prepared_samples(asset)
            original = self.assets.resolve(track.master)
            digest, size = digest_file(original)
            if (digest, size) != (asset.files[0].sha256, asset.files[0].size_bytes):
                raise ValueError("release master does not match the immutable asset bytes")
            if track.sha256 is not None and track.sha256 != digest:
                raise ValueError("release master hash differs from its actual bytes")
            if (track.sample_rate, track.channels, track.duration_samples) != (
                asset.probe.sample_rate,
                asset.probe.channels,
                asset.probe.duration_samples,
            ):
                raise ValueError("release master sample metadata differs from its actual asset")
            if track.commercial_use_status == "confirmed" and (
                asset.provenance.commercial_use != "confirmed"
                or asset.provenance.origin == "synthetic"
            ):
                raise ValueError("release rights claim conflicts with the asset's pending rights")
            tracks.append(
                ReleaseTrack.model_validate(
                    {
                        **track.model_dump(),
                        "sha256": digest,
                        "master": asset.files[0].location,
                    }
                )
            )
        saved = ReleaseRecord.model_validate({**record.model_dump(), "tracks": tracks})
        return self.store.save_draft(saved, expected_revision=expected_revision)
