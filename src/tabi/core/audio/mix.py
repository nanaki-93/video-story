"""One continuous float PCM soundtrack, then one AAC encode at final mux."""

import hashlib
import json
import math
import os
import re
import shutil
import tempfile
from contextlib import ExitStack
from fractions import Fraction
from pathlib import Path

import numpy as np

from ..assets.service import digest_file
from ..models.audio import AudioMixReport, AudioPreparation, AudioVerification
from ..models.base import AssetRef, content_hash
from ..models.production import Fingerprint
from ..process import run_tool
from ..render.backend import FrozenRegistry
from ..toolchain import doctor
from .pcm import BLOCK_SAMPLES, PCMReader, placement_block
from .timeline import prepared_samples, validate_placement


def audio_fingerprint():
    digest = hashlib.sha256()
    for path in sorted(Path(__file__).parent.glob("*.py")):
        digest.update(path.name.encode() + b"\0" + path.read_bytes())
    return Fingerprint(name="tabi-audio", version="1", sha256=digest.hexdigest())


def publish_media(temporary: Path, output: Path):
    with temporary.open("rb") as stream:
        os.fsync(stream.fileno())
    os.link(temporary, output)
    descriptor = os.open(output.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def probe_audio(settings, path):
    data = json.loads(
        run_tool(
            [
                settings.ffprobe,
                "-v",
                "error",
                "-select_streams",
                "a",
                "-show_streams",
                "-of",
                "json",
                str(path),
            ],
            timeout=300,
        )
    )
    if len(data.get("streams", [])) != 1:
        raise ValueError("expected exactly one audio stream")
    return data["streams"][0]


def measure_loudness(settings, path):
    # Analyze input metrics on a discarded output. Never replace or normalize the master/mix.
    output = run_tool(
        [
            settings.ffmpeg,
            "-hide_banner",
            "-v",
            "info",
            "-nostdin",
            "-i",
            str(path),
            "-af",
            "loudnorm=I=-14:TP=-1:LRA=11:print_format=json",
            "-f",
            "null",
            "-",
        ],
        timeout=3600,
        capture_stderr=True,
    ).decode("utf-8", errors="replace")
    matches = re.findall(r'\{\s*"input_i"[^}]+\}', output)
    if len(matches) != 1:
        raise ValueError("FFmpeg did not return the required input loudness measurement")
    values = json.loads(matches[0])

    def finite(name):
        value = float(values[name])
        return value if math.isfinite(value) else None

    return finite("input_i"), finite("input_tp"), finite("input_lra")


class AudioMixer:
    def __init__(self, assets, settings):
        self.assets, self.settings = assets, settings

    def _prepare(self, registry, root, stack):
        readers, preparations = {}, []
        for track in registry.snapshot.audio_placements:
            key = (track.asset.id, track.asset.version)
            asset = registry.get(track.asset, "asset")
            validate_placement(track, asset)
            if key in readers:
                continue
            index = len(readers)
            source = root / f"source-{index}.wav"
            shutil.copyfile(self.assets.resolve(asset.files[0].location), source)
            if digest_file(source) != (asset.files[0].sha256, asset.files[0].size_bytes):
                raise ValueError("source changed while preparing audio")
            with PCMReader(source) as original:
                if (original.samples, original.rate, original.channels) != (
                    asset.probe.duration_samples,
                    asset.probe.sample_rate,
                    asset.probe.channels,
                ):
                    raise ValueError("WAV header differs from the frozen asset")
            prepared = source
            count = prepared_samples(asset)
            if asset.probe.sample_rate != 48000:
                prepared = root / f"prepared-{index}.wav"
                run_tool(
                    [
                        self.settings.ffmpeg,
                        "-v",
                        "error",
                        "-xerror",
                        "-nostdin",
                        "-n",
                        "-i",
                        str(source),
                        "-map",
                        "0:a:0",
                        "-af",
                        f"aresample=48000:async=0:first_pts=0,apad=whole_len={count},atrim=end_sample={count}",
                        "-c:a",
                        "pcm_f64le",
                        "-ar",
                        "48000",
                        "-bitexact",
                        str(prepared),
                    ],
                    timeout=3600,
                )
            reader = stack.enter_context(PCMReader(prepared))
            if reader.samples != count or reader.rate != 48000:
                raise ValueError("prepared audio sample count differs from the rational target")
            readers[key] = reader
            preparations.append(
                AudioPreparation(
                    asset=AssetRef(id=asset.id, version=asset.version),
                    source_sha256=asset.files[0].sha256,
                    source_sample_rate=asset.probe.sample_rate,
                    source_samples=asset.probe.duration_samples,
                    prepared_samples=count,
                    resampled=asset.probe.sample_rate != 48000,
                )
            )
        return readers, preparations

    def render(self, snapshot, output: Path, *, start_sample=0, end_sample=None, gain_db=0.0):
        duration = snapshot.episode.fps.sample_at(snapshot.episode.duration_frames)
        end_sample = duration if end_sample is None else end_sample
        if (
            type(start_sample) is not int
            or type(end_sample) is not int
            or not 0 <= start_sample < end_sample <= duration
        ):
            raise ValueError("audio range must be nonempty and inside the episode sample interval")
        if isinstance(gain_db, bool) or not math.isfinite(gain_db) or not -120 <= gain_db <= 24:
            raise ValueError("explicit mix gain must be from -120 to +24 dB")
        output = output.expanduser().absolute()
        if output.suffix.lower() != ".wav" or output.exists() or output.is_symlink():
            raise ValueError("audio mix requires a new WAV output path")
        registry = FrozenRegistry(self.assets, snapshot)
        output.parent.mkdir(parents=True, exist_ok=True)
        capabilities = doctor(self.settings, output.parent)
        if not capabilities.ready:
            raise ValueError("media tools/storage are not ready; run tabi doctor")
        with (
            tempfile.TemporaryDirectory(prefix=".tabi-audio-", dir=output.parent) as scratch,
            ExitStack() as stack,
        ):
            root = Path(scratch)
            readers, preparations = self._prepare(registry, root, stack)
            raw, temporary = root / "continuous.f32", root / "mix.wav"
            peak, over = 0.0, 0
            digest = hashlib.sha256()
            placements = sorted(snapshot.audio_placements, key=lambda t: (t.start_sample, t.id))
            with raw.open("xb") as stream:
                for start in range(start_sample, end_sample, BLOCK_SAMPLES):
                    count = min(BLOCK_SAMPLES, end_sample - start)
                    mixed = np.zeros((count, 2), dtype=np.float64)
                    for track in placements:
                        if (
                            track.start_sample < start + count
                            and start < track.start_sample + track.duration_samples
                        ):
                            mixed += placement_block(
                                readers[(track.asset.id, track.asset.version)], track, start, count
                            )
                    mixed *= 10 ** (gain_db / 20)
                    if (
                        not np.all(np.isfinite(mixed))
                        or np.max(np.abs(mixed)) > np.finfo(np.float32).max
                    ):
                        raise ValueError(
                            "mixed samples cannot be represented as finite float32 PCM"
                        )
                    peak = max(peak, float(np.max(np.abs(mixed))))
                    over += int(np.count_nonzero(np.any(np.abs(mixed) > 1, axis=1)))
                    block = mixed.astype("<f4").tobytes()
                    digest.update(block)
                    stream.write(block)
            run_tool(
                [
                    self.settings.ffmpeg,
                    "-v",
                    "error",
                    "-nostdin",
                    "-n",
                    "-f",
                    "f32le",
                    "-ar",
                    "48000",
                    "-ac",
                    "2",
                    "-i",
                    str(raw),
                    "-c:a",
                    "pcm_f32le",
                    "-rf64",
                    "auto",
                    "-bitexact",
                    str(temporary),
                ],
                timeout=3600,
            )
            raw.unlink()
            stream = probe_audio(self.settings, temporary)
            expected = end_sample - start_sample
            if (
                stream.get("codec_name") != "pcm_f32le"
                or stream.get("sample_rate") != "48000"
                or stream.get("channels") != 2
                or int(stream["duration_ts"]) * Fraction(stream["time_base"]) * 48000 != expected
            ):
                raise ValueError("continuous PCM mix failed format/sample verification")
            decoded = root / "verified.f32"
            run_tool(
                [
                    self.settings.ffmpeg,
                    "-v",
                    "error",
                    "-xerror",
                    "-nostdin",
                    "-n",
                    "-i",
                    str(temporary),
                    "-f",
                    "f32le",
                    "-c:a",
                    "pcm_f32le",
                    str(decoded),
                ],
                timeout=3600,
            )
            if digest_file(decoded) != (digest.hexdigest(), expected * 8):
                raise ValueError("decoded PCM differs from the continuous sample mix")
            decoded.unlink()
            integrated, true_peak, loudness_range = measure_loudness(self.settings, temporary)
            warnings = []
            if peak == 0:
                warnings.append(
                    "The mixed range is digitally silent; no loudness target can be inferred."
                )
            if over:
                warnings.append(
                    "The float mix exceeds full scale; reduce explicit gain before AAC encoding."
                )
            if any(t.loop_duration_samples and not t.loop_crossfade_samples for t in placements):
                warnings.append("Ambience uses a hard loop; inspect its authored seam for clicks.")
            suggested = (
                min(-14 - integrated, -1 - true_peak)
                if integrated is not None and true_peak is not None
                else None
            )
            registry.verify()
            report = AudioMixReport(
                schema_version="1.0",
                snapshot_sha256=content_hash(snapshot),
                purpose=snapshot.purpose,
                first_sample=start_sample,
                sample_count=expected,
                output=str(output),
                output_sha256=digest_file(temporary)[0],
                backend=audio_fingerprint(),
                toolchain_fingerprint=capabilities.fingerprint,
                preparations=preparations,
                gain_db=float(gain_db),
                sample_peak_dbfs=20 * math.log10(peak) if peak else None,
                true_peak_dbtp=true_peak,
                integrated_lufs=integrated,
                loudness_range_lu=loudness_range,
                over_full_scale_samples=over,
                suggested_gain_db=suggested,
                warnings=warnings,
                verified_samples=True,
            )
            publish_media(temporary, output)
            return report


def verify_aac(settings, path: Path, expected_samples: int, scratch: Path):
    stream = probe_audio(settings, path)
    if (
        stream.get("codec_name") != "aac"
        or stream.get("sample_rate") != "48000"
        or stream.get("channels") != 2
        or abs(Fraction(stream.get("start_time", "0"))) > Fraction(1, 48000)
        or abs(
            int(stream["duration_ts"]) * Fraction(stream["time_base"]) * 48000 - expected_samples
        )
        > 1
    ):
        raise ValueError("AAC stream timing/format differs from the intended soundtrack")
    decoded = scratch / "aac-verification.f32"
    run_tool(
        [
            settings.ffmpeg,
            "-v",
            "error",
            "-xerror",
            "-nostdin",
            "-n",
            "-i",
            str(path),
            "-map",
            "0:a:0",
            "-f",
            "f32le",
            "-c:a",
            "pcm_f32le",
            str(decoded),
        ],
        timeout=3600,
    )
    samples, remainder = divmod(decoded.stat().st_size, 8)
    decoded.unlink()
    # AAC stores whole 1024-sample frames. Container duration/skip metadata carries the exact end.
    if remainder or not expected_samples <= samples <= expected_samples + 1023:
        raise ValueError("decoded AAC has unexpected truncation or padding")
    return AudioVerification(
        intended_samples=expected_samples,
        decoded_samples=samples,
        padding_samples=samples - expected_samples,
    )


def mux_aac(
    settings, video: Path, mix: Path, output: Path, *, expected_samples: int, scratch: Path
):
    run_tool(
        [
            settings.ffmpeg,
            "-v",
            "error",
            "-xerror",
            "-nostdin",
            "-n",
            "-i",
            str(video),
            "-i",
            str(mix),
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-movflags",
            "+faststart",
            str(output),
        ],
        timeout=3600,
    )
    return verify_aac(settings, output, expected_samples, scratch)
