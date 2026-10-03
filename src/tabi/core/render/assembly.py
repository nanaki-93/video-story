"""Verified video concat, explicit re-encode fallback and one continuous audio mux."""

import hashlib
import json
import os
import tempfile
import time
from fractions import Fraction
from pathlib import Path

from ..assets.service import digest_file
from ..audio.mix import AudioMixer, mux_aac, publish_media
from ..models.base import content_hash
from ..models.rendering import AssemblyInfo, RenderReport
from ..process import OperationCancelled, ToolError, checkpoint, run_tool
from ..toolchain import doctor
from .backend import FrozenRegistry, RenderError, backend_fingerprint
from .ffmpeg import verify_video


def stream_signature(settings, path):
    data = json.loads(
        run_tool(
            [
                settings.ffprobe,
                "-v",
                "error",
                "-show_streams",
                "-show_data_hash",
                "sha256",
                "-of",
                "json",
                str(path),
            ]
        )
    )
    if len(data.get("streams", [])) != 1 or data["streams"][0].get("codec_type") != "video":
        raise RenderError("assembly requires video-only chunks")
    stream = data["streams"][0]
    keys = (
        "codec_name",
        "codec_tag_string",
        "profile",
        "level",
        "width",
        "height",
        "pix_fmt",
        "color_range",
        "color_space",
        "color_transfer",
        "color_primaries",
        "time_base",
        "avg_frame_rate",
        "sample_aspect_ratio",
        "extradata_hash",
    )
    first = json.loads(
        run_tool(
            [
                settings.ffprobe,
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-read_intervals",
                "%+#1",
                "-show_packets",
                "-show_entries",
                "packet=flags",
                "-of",
                "json",
                str(path),
            ]
        )
    )
    keyframe = len(first.get("packets", [])) == 1 and "K" in first["packets"][0].get("flags", "")
    return {key: stream.get(key) for key in keys}, keyframe


class VideoAssembler:
    def __init__(self, assets, settings):
        self.assets, self.settings = assets, settings

    def render(self, snapshot, job, output, chunks):
        """Chunks are ordered (path, frame count, verified content hash) triples."""
        from ..jobs.planner import video_profile

        output = Path(output).absolute()
        if output.exists() or output.is_symlink():
            raise RenderError("assembled output exists; select a new path")
        if sum(count for _, count, _ in chunks) != job.duration_frames:
            raise RenderError("assembly chunk count differs from its frozen interval")
        registry = FrozenRegistry(self.assets, snapshot)
        profile = video_profile(job.profile)
        output.parent.mkdir(parents=True, exist_ok=True)
        capabilities = doctor(self.settings, output.parent)
        if not capabilities.ready or capabilities.fingerprint != job.plan.toolchain_fingerprint:
            raise RenderError("assembly toolchain differs from the frozen job or is unavailable")
        began = time.monotonic()
        with tempfile.TemporaryDirectory(prefix=".tabi-assembly-", dir=output.parent) as scratch:
            root = Path(scratch)
            manifest, signatures = ["ffconcat version 1.0"], []
            for index, (path, frames, digest) in enumerate(chunks):
                checkpoint()
                if digest_file(path)[0] != digest:
                    raise RenderError("chunk changed before assembly")
                local = root / f"{index:08}.mp4"
                os.link(path, local)
                signatures.append(stream_signature(self.settings, local))
                # User paths never enter FFmpeg's concat language. It sees only
                # owned, numeric ASCII basenames in this private directory.
                duration_us = round(Fraction(frames * profile.fps.den * 1000000, profile.fps.num))
                manifest.extend([f"file {local.name}", f"duration {duration_us / 1000000:.6f}"])
            text = "\n".join(manifest) + "\n"
            manifest_path = root / "inputs.ffconcat"
            manifest_path.write_text(text)
            video = root / "assembled-video.mp4"
            mode, reason = "stream_copy", None
            compatible = all(
                keyframe and signature == signatures[0][0] for signature, keyframe in signatures
            )
            base = [
                self.settings.ffmpeg,
                "-v",
                "error",
                "-xerror",
                "-nostdin",
                "-n",
                "-f",
                "concat",
                "-safe",
                "1",
                "-i",
                str(manifest_path),
                "-map",
                "0:v:0",
                "-an",
            ]
            if compatible:
                try:
                    run_tool(
                        [*base, "-c:v", "copy", "-movflags", "+faststart", str(video)], timeout=3600
                    )
                    verify_video(self.settings, video, profile, job.duration_frames)
                except OperationCancelled:
                    raise
                except (ToolError, RenderError) as error:
                    reason = f"Stream copy failed verification: {error}"
            else:
                reason = "Chunk codec configuration or initial keyframes require re-encoding."
            if reason:
                mode = "reencode"
                video.unlink(missing_ok=True)
                args = [
                    *base,
                    "-vf",
                    f"setpts=N*{profile.fps.den}/({profile.fps.num}*TB)",
                    "-r",
                    f"{profile.fps.num}/{profile.fps.den}",
                    "-fps_mode",
                    "cfr",
                    "-c:v",
                    profile.video_codec,
                    "-g",
                    "60",
                    "-pix_fmt",
                    "yuv420p",
                ]
                if profile.video_codec == "libx264":
                    args.extend(
                        ["-preset", "veryfast", "-flags", "+cgop", "-x264-params", "open-gop=0"]
                    )
                    args.extend(
                        ["-b:v", str(profile.video_bitrate)]
                        if profile.video_bitrate
                        else ["-crf", "16"]
                    )
                else:
                    args.extend(["-allow_sw", "0", "-b:v", str(profile.video_bitrate or 8000000)])
                args.extend(
                    [
                        "-color_range",
                        "tv",
                        "-colorspace",
                        "bt709",
                        "-color_primaries",
                        "bt709",
                        "-color_trc",
                        "bt709",
                        "-movflags",
                        "+faststart",
                        str(video),
                    ]
                )
                run_tool(args, timeout=3600)
                verify_video(self.settings, video, profile, job.duration_frames)
            final, audio, audio_verified = video, None, None
            if job.profile.audio_codec:
                audio_path = root / "continuous.wav"
                audio = AudioMixer(self.assets, self.settings).render(
                    snapshot,
                    audio_path,
                    start_sample=job.profile.fps.sample_at(job.first_frame),
                    end_sample=job.profile.fps.sample_at(job.first_frame + job.duration_frames),
                    gain_db=job.profile.audio_gain_db,
                )
                if audio.over_full_scale_samples:
                    raise RenderError(
                        "mix exceeds full scale; reduce explicit audio gain before export"
                    )
                final = root / "final.mp4"
                audio_verified = mux_aac(
                    self.settings,
                    video,
                    audio_path,
                    final,
                    expected_samples=audio.sample_count,
                    scratch=root,
                )
                audio = audio.model_copy(update={"output": None})
            verify_video(self.settings, final, job.profile, job.duration_frames)
            registry.verify()
            if doctor(self.settings, output.parent).fingerprint != capabilities.fingerprint:
                raise RenderError("media toolchain changed during assembly")
            for path, _, digest in chunks:
                if digest_file(path)[0] != digest:
                    raise RenderError("chunk changed during assembly")
            output_digest, size = digest_file(final)
            report = RenderReport(
                schema_version="1.0",
                purpose=snapshot.purpose,
                snapshot_sha256=content_hash(snapshot),
                first_frame=job.first_frame,
                frame_count=job.duration_frames,
                canvas=job.profile.canvas,
                fps=job.profile.fps,
                output=str(output),
                output_sha256=output_digest,
                output_bytes=size,
                graph_sha256=hashlib.sha256(text.encode()).hexdigest(),
                backend=backend_fingerprint(),
                toolchain_fingerprint=job.plan.toolchain_fingerprint,
                render_seconds=time.monotonic() - began,
                full_decode_passed=True,
                timestamps_verified=True,
                normalized_images=0,
                audio_mix=audio,
                audio_verification=audio_verified,
                assembly=AssemblyInfo(
                    mode=mode,
                    chunk_sha256=[digest for _, _, digest in chunks],
                    fallback_reason=reason,
                ),
            )
            checkpoint(force=True)
            publish_media(final, output)
            return report
