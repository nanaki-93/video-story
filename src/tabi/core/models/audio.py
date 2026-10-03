"""Observed waveform and sample timeline contracts; no audio/master modification."""

from typing import Literal, Self

from pydantic import Field, model_validator

from .base import SHA256, AssetRef, Document, Frame, Model, Number, PositiveInt
from .episode import TrackPlacement
from .production import ValidationIssue


class SampleRange(Model):
    start_sample: Frame
    end_sample: Frame

    @model_validator(mode="after")
    def nonempty(self) -> Self:
        if self.end_sample <= self.start_sample:
            raise ValueError("sample interval must be nonempty and half-open")
        return self


class WaveformBin(SampleRange):
    minimum: list[Number] = Field(min_length=1, max_length=2)
    maximum: list[Number] = Field(min_length=1, max_length=2)
    rms: list[Number] = Field(min_length=1, max_length=2)


class WaveformReport(Document):
    document_type: Literal["waveform_report"] = "waveform_report"
    asset: AssetRef
    asset_content_sha256: SHA256
    source_sha256: SHA256
    sample_rate: PositiveInt
    duration_samples: PositiveInt
    channels: Literal[1, 2]
    bins: list[WaveformBin] = Field(min_length=1, max_length=8192)
    leading_silence_samples: Frame
    trailing_silence_samples: Frame
    silent: bool
    synthetic: bool

    @model_validator(mode="after")
    def coverage(self) -> Self:
        cursor = 0
        for item in self.bins:
            if item.start_sample != cursor:
                raise ValueError("waveform bins must be contiguous")
            if any(len(v) != self.channels for v in (item.minimum, item.maximum, item.rms)):
                raise ValueError("waveform channel count differs from source")
            if any(
                low < -1 or high > 1 or low > high or rms < 0 or rms > 1
                for low, high, rms in zip(item.minimum, item.maximum, item.rms, strict=True)
            ):
                raise ValueError("waveform values must describe normalized PCM")
            cursor = item.end_sample
        if cursor != self.duration_samples:
            raise ValueError("waveform bins must cover the source")
        if max(self.leading_silence_samples, self.trailing_silence_samples) > cursor:
            raise ValueError("silence exceeds the source")
        return self


class AudioTimelineReport(Document):
    document_type: Literal["audio_timeline_report"] = "audio_timeline_report"
    sample_rate: Literal[48000] = 48000
    duration_samples: PositiveInt
    placements: list[TrackPlacement]
    music_gaps: list[SampleRange]
    issues: list[ValidationIssue]
