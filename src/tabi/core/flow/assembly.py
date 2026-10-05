"""Frozen complete-scene export using the existing verified media primitives."""

import hashlib
import json
import tempfile
from pathlib import Path
from uuid import uuid4

from ..assets import AssetService
from ..assets.service import digest_file
from ..audio.mix import AudioMixer, mux_aac, publish_media
from ..models.base import (
    FrameInterval,
    HashedFile,
    MediaPath,
    ResolvedAssetLock,
    content_hash,
)
from ..models.flow import FlowExport, FlowExportInputs, FlowSegment
from ..models.production import OutputProfile
from ..process import OperationCancelled, checkpoint, run_tool
from ..render.assembly import concatenate_video
from ..render.ffmpeg import verify_video
from ..render.profiles import require_encoder, video_arguments
from ..toolchain import doctor
from .runner import export_ranges
from .service import FlowError, updated


def flow_fingerprint():
    digest = hashlib.sha256()
    for path in [
        Path(__file__),
        Path(__file__).parents[1] / "render/assembly.py",
        Path(__file__).parents[1] / "audio/mix.py",
    ]:
        digest.update(path.name.encode() + b"\0" + path.read_bytes())
    return digest.hexdigest()


class FlowAssembler:
    def __init__(self, service, settings):
        self.service, self.settings = service, settings

    def freeze(self, episode_id, *, revision, profile=None, tracks=None):
        episode = self.service.get(episode_id)
        if episode.revision != revision:
            raise FlowError("Video changed; reload before exporting.")
        ranges = export_ranges(episode)
        first = ranges[0][0]
        profile = profile or OutputProfile(
            id="flow-native-youtube",
            canvas=first.canvas,
            fps=first.fps,
            container="mp4",
            video_codec="libx264",
            pixel_format="yuv420p",
            color_space="bt709",
        )
        tracks = tracks or []
        if profile.fps != episode.recipe.fps or profile.audio_codec not in {None, "aac"}:
            raise FlowError("Use the native frame rate and AAC for an optional soundtrack.")
        profile = updated(profile, audio_codec="aac" if tracks else None)
        assets = AssetService(
            self.service.store,
            roots=self.service.media_roots,
            ffmpeg=self.settings.ffmpeg,
            ffprobe=self.settings.ffprobe,
        )
        locked_audio = {}
        for track in tracks:
            asset = assets.require_valid(track.asset)
            if asset.kind != "audio":
                raise FlowError("Choose a local PCM WAV master for the soundtrack.")
            locked_audio[(asset.id, asset.version)] = ResolvedAssetLock(
                id=asset.id, version=asset.version, sha256=content_hash(asset)
            )
        for candidate, _, _ in ranges:
            self.service.verify_file(candidate.media)
            if candidate.canvas != first.canvas or candidate.fps != first.fps:
                raise FlowError("Accepted clips have incompatible canvases or frame rates.")
        for reference in episode.references:
            self.service.verify_file(reference.media)
        capabilities = doctor(self.settings, self.service.store.root / "exports")
        if not capabilities.ready:
            raise FlowError("Media tools are unavailable; run setup-check.")
        require_encoder(capabilities, profile)
        inputs = FlowExportInputs(
            episode_id=episode.id,
            episode_revision=episode.revision,
            recipe_sha256=content_hash(episode.recipe),
            references=episode.references,
            segments=[
                FlowSegment(
                    candidate_id=candidate.id,
                    media=candidate.media,
                    trim=FrameInterval(start_frame=start, end_frame=end),
                    observed_state=candidate.observed_state,
                )
                for candidate, start, end in ranges
            ],
            profile=profile,
            duration_frames=episode.recipe.target_frames,
            tracks=tracks,
            audio_locks=list(locked_audio.values()),
            pipeline_sha256=flow_fingerprint(),
            toolchain_sha256=capabilities.fingerprint,
        )
        export = FlowExport(
            schema_version="1.0",
            id=uuid4().hex,
            episode_id=episode.id,
            inputs=inputs,
            inputs_sha256=content_hash(inputs),
            state="queued",
        )
        self.service._immutable(f"flow/exportepisodes/{export.id}.json", episode)
        return self.service.save_export(export, expected_revision=None)

    def run(self, export_id, *, owner=None):
        export = self.service.get_export(export_id)
        with self.service.store.exclusive_lock(f"flow/locks/{export.id}.lock"):
            export = self.service.get_export(export_id)
            if export.state == "verified":
                self.service.verify_file(export.output)
                return export
            if export.cancel_requested or export.state == "cancelled":
                raise FlowError("This export was cancelled. Create a new export when ready.")
            export = self.service.save_export(
                updated(export, state="running", owner=owner or uuid4().hex, diagnostic=None),
                expected_revision=export.revision,
            )
            try:
                return self._render(export)
            except BaseException as error:
                latest = self.service.get_export(export.id)
                state = "cancelled" if isinstance(error, OperationCancelled) else "failed"
                self.service.save_export(
                    updated(
                        latest,
                        state=state,
                        diagnostic=str(error) or type(error).__name__,
                        owner=None,
                    ),
                    expected_revision=latest.revision,
                )
                raise

    def _render(self, export):
        inputs = export.inputs
        output = self.service.store.root / "exports" / f"{export.id}.mp4"
        report_path = f"flow/reports/{export.id}.json"
        capabilities = doctor(self.settings, output.parent)
        if (
            capabilities.fingerprint != inputs.toolchain_sha256
            or flow_fingerprint() != inputs.pipeline_sha256
        ):
            raise FlowError("Export pipeline or media tools changed; prepare a new export.")
        for segment in inputs.segments:
            self.service.verify_file(segment.media)
        for reference in inputs.references:
            self.service.verify_file(reference.media)
        if output.exists():
            report = json.loads(self.service.store._read_bytes(report_path))
            if (
                report["inputs_sha256"] != export.inputs_sha256
                or digest_file(output)[0] != report["output_sha256"]
            ):
                raise FlowError("Existing output does not match this frozen export.")
            verify_video(self.settings, output, inputs.profile, inputs.duration_frames)
            return self._finish(export, output, report_path)
        with tempfile.TemporaryDirectory(prefix=".flow-export-", dir=output.parent) as temporary:
            root = Path(temporary)
            chunks = []
            video_profile = updated(inputs.profile, audio_codec=None)
            for index, segment in enumerate(inputs.segments):
                checkpoint()
                source = self.service.verify_file(segment.media)
                profile, trim = inputs.profile, segment.trim
                frames = trim.end_frame - trim.start_frame
                local = root / f"prepared-{index}.mp4"
                graph = (
                    f"trim=start_frame={trim.start_frame}:end_frame={trim.end_frame},"
                    f"setpts=N*{profile.fps.den}/({profile.fps.num}*TB),"
                    f"scale={profile.canvas.width}:{profile.canvas.height}:out_color_matrix=bt709,"
                    "setsar=1,setparams=range=limited:color_primaries=bt709:"
                    "color_trc=bt709:colorspace=bt709"
                )
                run_tool(
                    [
                        self.settings.ffmpeg,
                        "-v",
                        "error",
                        "-xerror",
                        "-nostdin",
                        "-protocol_whitelist",
                        "file,pipe",
                        "-i",
                        str(source),
                        "-map",
                        "0:v:0",
                        "-an",
                        "-vf",
                        graph,
                        "-r",
                        f"{profile.fps.num}/{profile.fps.den}",
                        *video_arguments(profile),
                        str(local),
                    ],
                    timeout=3600,
                )
                verify_video(self.settings, local, video_profile, frames)
                chunks.append((local, frames, digest_file(local)[0]))
            video, mode, reason, manifest = concatenate_video(
                self.settings, video_profile, chunks, root, inputs.duration_frames
            )
            audio = None
            if inputs.tracks:
                assets = AssetService(
                    self.service.store,
                    roots=self.service.media_roots,
                    ffmpeg=self.settings.ffmpeg,
                    ffprobe=self.settings.ffprobe,
                )
                mix_path = root / "continuous.wav"
                mix = AudioMixer(assets, self.settings).render_tracks(
                    inputs.tracks,
                    inputs.audio_locks,
                    inputs.profile.fps.sample_at(inputs.duration_frames),
                    export.inputs_sha256,
                    mix_path,
                    gain_db=inputs.profile.audio_gain_db,
                )
                if mix.over_full_scale_samples:
                    raise FlowError("Soundtrack exceeds full scale; review its explicit gain.")
                final = root / "with-audio.mp4"
                audio_verification = mux_aac(
                    self.settings,
                    video,
                    mix_path,
                    final,
                    expected_samples=mix.sample_count,
                    scratch=root,
                    bitrate=inputs.profile.audio_bitrate,
                )
                video = final
                audio = {
                    "mix": {**mix.model_dump(mode="json"), "output": None},
                    "verification": audio_verification.model_dump(mode="json"),
                }
            verification = verify_video(
                self.settings, video, inputs.profile, inputs.duration_frames
            )
            for segment in inputs.segments:
                self.service.verify_file(segment.media)
            for reference in inputs.references:
                self.service.verify_file(reference.media)
            if doctor(self.settings, output.parent).fingerprint != inputs.toolchain_sha256:
                raise FlowError("Media tools changed during export.")
            digest, size = digest_file(video)
            report = {
                "schema_version": "1.0",
                "export_id": export.id,
                "inputs_sha256": export.inputs_sha256,
                "output_sha256": digest,
                "output_bytes": size,
                "video": verification.model_dump(mode="json"),
                "assembly_mode": mode,
                "fallback_reason": reason,
                "manifest_sha256": hashlib.sha256(manifest.encode()).hexdigest(),
                "source_hashes": [segment.media.sha256 for segment in inputs.segments],
                "preparation": (
                    "Reviewed video-only H.264 trims with continuous timestamps and BT.709 tags."
                ),
                "scaling": inputs.profile.canvas.model_dump(mode="json"),
                "synthetic": self._synthetic(export),
                "creative_approval": "pending",
                "audio": audio,
            }
            with self.service.store.writer_lock():
                self.service.store._atomic_write(
                    report_path, json.dumps(report).encode(), overwrite=True
                )
            checkpoint(force=True)
            publish_media(video, output)
            return self._finish(export, output, report_path)

    def _synthetic(self, export):
        episode = self.service.store.read(f"flow/exportepisodes/{export.id}.json")
        candidates = {item.id: item for item in episode.candidates}
        assets = [
            self.service.store.read(
                f"registry/assets/flow-{candidates[item.candidate_id].attempt_id}/1.0.json"
            )
            for item in export.inputs.segments
        ]
        return any(reference.synthetic for reference in export.inputs.references) or any(
            asset.provenance.origin == "synthetic" for asset in assets
        )

    def _finish(self, export, output, report_path):
        export = self.service.get_export(export.id)
        if export.cancel_requested:
            raise OperationCancelled("the owned export was cancelled")
        digest, size = digest_file(output)
        return self.service.save_export(
            updated(
                export,
                state="verified",
                owner=None,
                output=HashedFile(
                    location=MediaPath(path=f"exports/{export.id}.mp4"),
                    sha256=digest,
                    size_bytes=size,
                ),
                report_path=report_path,
            ),
            expected_revision=export.revision,
        )
