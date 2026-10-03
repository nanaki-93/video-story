"""Pure audio placement validation; source trims refer to the prepared 48 kHz stream."""

from fractions import Fraction

from ..models import Asset, Episode, TrackPlacement
from ..models.audio import AudioTimelineReport, SampleRange
from ..models.production import ValidationIssue


def prepared_samples(asset: Asset) -> int:
    if (
        asset.kind != "audio"
        or len(asset.files) != 1
        or asset.probe.channels not in {1, 2}
        or not asset.probe.sample_rate
        or not asset.probe.duration_samples
    ):
        raise ValueError("audio requires one mono/stereo WAV master with exact sample metadata")
    return round(Fraction(asset.probe.duration_samples * 48000, asset.probe.sample_rate))


def validate_placement(placement: TrackPlacement, asset: Asset) -> None:
    if placement.trim_end_sample > prepared_samples(asset):
        raise ValueError(f"track {placement.id}: trim exceeds the prepared source sample count")


def inspect_timeline(episode: Episode, resolve) -> AudioTimelineReport:
    episode = Episode.model_validate(episode)
    duration = episode.fps.sample_at(episode.duration_frames)
    ordered = sorted(episode.tracks, key=lambda track: (track.start_sample, track.id))
    issues, gaps = [], []
    cursor = 0
    for track in ordered:
        asset = resolve(track.asset)
        validate_placement(track, asset)
        if asset.probe.sample_rate != 48000:
            issues.append(
                ValidationIssue(
                    severity="info",
                    code="audio_resample",
                    location=["tracks", track.id],
                    message=f"{asset.probe.sample_rate} Hz master needs a separate 48000 Hz copy.",
                    suggested_fix="Review the prepared playback; the master stays unchanged.",
                )
            )
        if track.role != "music":
            continue
        if track.start_sample > cursor:
            gaps.append(SampleRange(start_sample=cursor, end_sample=track.start_sample))
        elif track.start_sample < cursor:
            issues.append(
                ValidationIssue(
                    severity="warning",
                    code="music_overlap",
                    location=["tracks", track.id],
                    message="Music placements overlap and their samples will be added.",
                    suggested_fix="Confirm the authored crossfade and review the mixed peak.",
                )
            )
        cursor = max(cursor, track.start_sample + track.duration_samples)
    if cursor < duration:
        gaps.append(SampleRange(start_sample=cursor, end_sample=duration))
    for gap in gaps:
        issues.append(
            ValidationIssue(
                severity="warning",
                code="music_gap",
                location=["tracks", gap.start_sample],
                message=f"No music placement covers samples [{gap.start_sample},{gap.end_sample}).",
                suggested_fix="Confirm intentional silence or edit the music placements.",
            )
        )
    return AudioTimelineReport(
        schema_version="1.0",
        duration_samples=duration,
        placements=ordered,
        music_gaps=gaps,
        issues=issues,
    )
