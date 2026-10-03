"""Bounded PCM reads and an explicit linear sample envelope, shared by preview/mix."""

import wave
from pathlib import Path

import numpy as np

from ..models.episode import TrackPlacement

BLOCK_SAMPLES = 65536


def decode_pcm(data: bytes, width: int, channels: int) -> np.ndarray:
    if width not in {1, 2, 3, 4} or channels not in {1, 2}:
        raise ValueError("prepared audio requires 8/16/24/32-bit PCM, mono or stereo")
    if len(data) % (width * channels):
        raise ValueError("truncated PCM sample")
    if width == 1:
        values = np.frombuffer(data, dtype=np.uint8).astype(np.float64) - 128
    elif width == 3:
        raw = np.frombuffer(data, dtype=np.uint8).reshape(-1, 3).astype(np.int32)
        values = raw[:, 0] | (raw[:, 1] << 8) | (raw[:, 2] << 16)
        values = np.where(values & 0x800000, values - 0x1000000, values)
    else:
        values = np.frombuffer(data, dtype=f"<i{width}").astype(np.float64)
    return (values / (2 ** (width * 8 - 1))).reshape(-1, channels)


class PCMReader:
    def __init__(self, path: Path):
        try:
            self.stream = wave.open(str(path), "rb")
        except (wave.Error, EOFError) as error:
            raise ValueError("use an uncompressed integer PCM WAV master") from error
        self.rate = self.stream.getframerate()
        self.channels = self.stream.getnchannels()
        self.width = self.stream.getsampwidth()
        self.samples = self.stream.getnframes()
        if self.channels not in {1, 2} or self.width not in {1, 2, 3, 4} or not self.samples:
            self.stream.close()
            raise ValueError("use nonempty mono/stereo PCM WAV masters")

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.stream.close()

    def read(self, start: int, count: int) -> np.ndarray:
        if type(start) is not int or type(count) is not int or not 0 <= start <= self.samples:
            raise ValueError("PCM range must use nonnegative integer sample positions")
        if not 0 <= count <= BLOCK_SAMPLES or start + count > self.samples:
            raise ValueError("PCM block exceeds source or bounded block size")
        self.stream.setpos(start)
        data = self.stream.readframes(count)
        if len(data) != count * self.width * self.channels:
            raise ValueError("truncated PCM source")
        return decode_pcm(data, self.width, self.channels)


def placement_block(
    reader: PCMReader, placement: TrackPlacement, start_sample: int, count: int
) -> np.ndarray:
    """Return stereo float64 for a global range without cumulative phase or rounding.

    An N-sample fade includes both endpoints: index 0 is zero and N-1 is full
    gain. A one-sample fade mutes that endpoint. No clipping/normalization occurs.
    """
    if (
        type(start_sample) is not int
        or start_sample < 0
        or type(count) is not int
        or not 0 <= count <= BLOCK_SAMPLES
    ):
        raise ValueError("invalid bounded audio range")
    if reader.rate != 48000 or placement.trim_end_sample > reader.samples:
        raise ValueError("placement requires a prepared 48 kHz source of sufficient length")
    result = np.zeros((count, 2), dtype=np.float64)
    first = max(start_sample, placement.start_sample)
    end = min(start_sample + count, placement.start_sample + placement.duration_samples)
    if end <= first:
        return result
    offset = first - placement.start_sample
    samples = reader.read(placement.trim_start_sample + offset, end - first)
    positions = np.arange(offset, offset + len(samples), dtype=np.int64)
    envelope = np.ones(len(samples), dtype=np.float64)
    if placement.fade_in_samples:
        envelope *= np.minimum(1, positions / max(1, placement.fade_in_samples - 1))
    if placement.fade_out_samples:
        envelope *= np.minimum(
            1, (placement.duration_samples - 1 - positions) / max(1, placement.fade_out_samples - 1)
        )
    samples *= envelope[:, None] * 10 ** (placement.gain_db / 20)
    result[first - start_sample : end - start_sample] = samples
    return result
