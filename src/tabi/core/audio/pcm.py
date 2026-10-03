"""Bounded PCM reads and an explicit linear sample envelope, shared by preview/mix."""

import struct
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
        self.stream = path.open("rb")
        try:
            self._header(path.stat().st_size)
        except BaseException:
            self.stream.close()
            raise

    def _header(self, size):
        header = self.stream.read(12)
        if len(header) != 12 or header[:4] not in {b"RIFF", b"RF64"} or header[8:] != b"WAVE":
            raise ValueError("use an uncompressed little-endian PCM/float WAV master")
        riff_size = int.from_bytes(header[4:8], "little")
        limit = riff_size + 8 if header[:4] == b"RIFF" else size
        if limit > size:
            raise ValueError("truncated WAV container")
        format_data, audio_data, extended_size = None, None, None
        cursor = 12
        while cursor + 8 <= limit:
            self.stream.seek(cursor)
            tag, length = struct.unpack("<4sI", self.stream.read(8))
            if tag == b"ds64" and header[:4] == b"RF64":
                if length < 28 or cursor + 8 + length > size:
                    raise ValueError("invalid RF64 size header")
                rf_size, extended_size, _, _ = struct.unpack("<QQQI", self.stream.read(28))
                limit = rf_size + 8
                if limit > size:
                    raise ValueError("truncated RF64 container")
            if tag == b"data" and length == 0xFFFFFFFF:
                if extended_size is None:
                    raise ValueError("RF64 data needs an explicit 64-bit sample size")
                length = extended_size
            if cursor + 8 + length > limit:
                raise ValueError("truncated WAV chunk")
            if tag == b"fmt ":
                if format_data is not None or not 16 <= length <= 64:
                    raise ValueError("unsupported/duplicate WAV format header")
                format_data = self.stream.read(length)
            elif tag == b"data":
                if audio_data is not None:
                    raise ValueError("WAV master must have one contiguous data chunk")
                audio_data = (cursor + 8, length)
            cursor += 8 + length + (length % 2)
        if format_data is None or audio_data is None:
            raise ValueError("WAV lacks its format or PCM samples")
        code, self.channels, self.rate, byte_rate, alignment, bits = struct.unpack(
            "<HHIIHH", format_data[:16]
        )
        if code == 0xFFFE:
            if len(format_data) < 40 or int.from_bytes(format_data[16:18], "little") < 22:
                raise ValueError("truncated extensible WAV format")
            valid_bits = int.from_bytes(format_data[18:20], "little")
            mask = int.from_bytes(format_data[20:24], "little")
            if valid_bits != bits or mask not in ({0, 4} if self.channels == 1 else {0, 3}):
                raise ValueError("WAV valid bits/channel mask requires explicit preparation")
            guid = format_data[24:40]
            if guid[4:] != bytes.fromhex("00001000800000aa00389b71"):
                raise ValueError("compressed WAV subformats require external preparation")
            code = int.from_bytes(guid[:4], "little")
        self.width = bits // 8
        if (
            self.channels not in {1, 2}
            or self.rate <= 0
            or bits % 8
            or (code == 1 and self.width not in {1, 2, 3, 4})
            or (code == 3 and self.width not in {4, 8})
            or code not in {1, 3}
            or alignment != self.width * self.channels
            or byte_rate != self.rate * alignment
        ):
            raise ValueError("use mono/stereo integer PCM or IEEE float WAV masters")
        self.floating = code == 3
        self.data_offset, self.data_bytes = audio_data
        self.samples, remainder = divmod(self.data_bytes, alignment)
        if remainder or not self.samples:
            raise ValueError("WAV data must contain complete nonempty PCM samples")
        self.codec = (
            f"pcm_f{bits}le" if self.floating else ("pcm_u8" if bits == 8 else f"pcm_s{bits}le")
        )

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.stream.close()

    def read(self, start: int, count: int) -> np.ndarray:
        if type(start) is not int or type(count) is not int or not 0 <= start <= self.samples:
            raise ValueError("PCM range must use nonnegative integer sample positions")
        if not 0 <= count <= BLOCK_SAMPLES or start + count > self.samples:
            raise ValueError("PCM block exceeds source or bounded block size")
        self.stream.seek(self.data_offset + start * self.width * self.channels)
        data = self.stream.read(count * self.width * self.channels)
        if len(data) != count * self.width * self.channels:
            raise ValueError("truncated PCM source")
        if self.floating:
            result = np.frombuffer(data, dtype=f"<f{self.width}").astype(np.float64)
            if not np.all(np.isfinite(result)):
                raise ValueError("WAV contains nonfinite floating-point samples")
            return result.reshape(-1, self.channels)
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
    if placement.loop_duration_samples is None:
        samples = reader.read(placement.trim_start_sample + offset, end - first)
    else:
        samples = loop_block(reader, placement, offset, end - first)
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


def loop_block(reader, placement, offset, count):
    """Linear tail/head overlap, with a persistent global period of length - crossfade."""
    crossfade = placement.loop_crossfade_samples
    period = placement.source_samples - crossfade
    result = np.empty((count, reader.channels), dtype=np.float64)
    cursor = 0
    while cursor < count:
        absolute = offset + cursor
        phase = absolute % period
        length = min(count - cursor, period - phase)
        block = reader.read(placement.trim_start_sample + phase, length)
        if absolute >= period and phase < crossfade:
            overlap = min(length, crossfade - phase)
            tail = reader.read(placement.trim_start_sample + period + phase, overlap)
            weights = np.arange(phase, phase + overlap, dtype=np.float64) / (crossfade - 1)
            block[:overlap] = tail * (1 - weights[:, None]) + block[:overlap] * weights[:, None]
        result[cursor : cursor + length] = block
        cursor += length
    return result
