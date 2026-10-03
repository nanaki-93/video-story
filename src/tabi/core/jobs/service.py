"""Single-worker durable queue, owned execution and verified artifact publication."""

import hashlib
import os
import stat
import tempfile
import time
from pathlib import Path
from uuid import uuid4

from ..audio.mix import verify_aac
from ..cache.keys import video_descriptor
from ..cache.storage import estimate_storage
from ..cache.store import CacheStore
from ..models.base import HashedFile, MediaPath, canonical_bytes, content_hash, relative_path
from ..models.production import JobError, OutputProfile, RenderJob
from ..models.rendering import CacheReuse, RenderReport
from ..process import ExecutionScope, OperationCancelled, ToolError, checkpoint, execution_scope
from ..render.assembly import VideoAssembler
from ..render.backend import FrozenRegistry, backend_fingerprint
from ..render.ffmpeg import FFmpegRenderer, verify_video
from ..toolchain import doctor
from .ledger import JobLedger, revised
from .planner import pipeline_fingerprint, plan_chunks, video_profile


class JobOwnershipError(ValueError):
    pass


class JobService:
    def __init__(self, assets, settings, *, on_process=None):
        self.assets, self.store, self.settings = assets, assets.store, settings
        self.ledger = JobLedger(self.store)
        self.owner = f"worker-{uuid4().hex}"
        self.on_process = on_process

    def submit(
        self, digest, profile, destination, *, first_frame=0, end_frame=None, max_chunk_frames=None
    ):
        snapshot = self.store.read_snapshot(digest)
        FrozenRegistry(self.assets, snapshot)
        profile = OutputProfile.model_validate(profile)
        end = snapshot.episode.duration_frames if end_frame is None else end_frame
        if (
            type(first_frame) is not int
            or type(end) is not int
            or not 0 <= first_frame < end <= snapshot.episode.duration_frames
        ):
            raise ValueError("job interval must be inside its frozen episode")
        if profile.fps != snapshot.episode.fps:
            raise ValueError("job profile fps must match its snapshot")
        destination = relative_path(destination)
        if not destination.startswith("exports/") or Path(destination).suffix.lower() != ".mp4":
            raise ValueError("job output must be a new MP4 beneath the project's exports folder")
        parts = self.store._parts(destination)
        with self.store._directory(parts[:-1], create=True) as directory:
            try:
                os.stat(parts[-1], dir_fd=directory, follow_symlinks=False)
            except FileNotFoundError:
                pass
            else:
                raise ValueError("job destination already exists; select a new path")
        plan, chunks = plan_chunks(snapshot, profile, first_frame, end, max_frames=max_chunk_frames)
        job = RenderJob(
            schema_version="1.0",
            document_type="render_job",
            id=f"job-{uuid4().hex}",
            snapshot_sha256=digest,
            profile=profile,
            backend=backend_fingerprint(),
            state="queued",
            duration_frames=end - first_frame,
            first_frame=first_frame,
            destination=destination,
            chunks=chunks,
            plan=plan,
        )
        return self.ledger.create(job)

    def cancel(self, identity):
        def request(job):
            if job.state in {"verified", "failed", "cancelled"}:
                return job
            if job.state == "running":
                return revised(job, cancel_requested=True)
            return revised(job, state="cancelled", cancel_requested=True, owner=None)

        return self.ledger.update(identity, "cancel_requested", request)

    def _owned(self, job):
        if job.owner != self.owner or job.state != "running":
            raise JobOwnershipError("this worker does not own the running job")
        return job

    def _cancelled(self, identity):
        return self._owned(self.ledger.get(identity)).cancel_requested

    def _recover(self):
        recovered = []
        for job in self.ledger.all():
            if job.state == "running":

                def interrupted(current):
                    chunks = [
                        chunk.model_copy(update={"state": "pending"})
                        if chunk.state == "rendering"
                        else chunk
                        for chunk in current.chunks
                    ]
                    return revised(
                        current,
                        state="interrupted",
                        owner=None,
                        chunks=chunks,
                        error=JobError(
                            code="worker_interrupted",
                            message=(
                                "The previous worker ended before completion. "
                                "Verified chunks are retained; "
                                "no saved PID was adopted or signalled."
                            ),
                        ),
                    )

                job = self.ledger.update(job.id, "interrupted", interrupted)
                recovered.append(job)
            self.ledger.checkpoint(job.id)
        return recovered

    def recover(self):
        with self.store.exclusive_lock(".tabi-worker.lock"):
            return self._recover()

    def _validate_plan(self, job):
        if job.plan is None:
            raise ValueError("legacy job has no frozen chunk plan; submit a new job")
        if job.backend != backend_fingerprint() or job.plan.pipeline != pipeline_fingerprint():
            raise ValueError("render pipeline changed since submission; create a new job")
        if job.plan.profile_sha256 != content_hash(job.profile):
            raise ValueError("job output profile differs from its frozen plan")
        snapshot = self.store.read_snapshot(job.snapshot_sha256)
        FrozenRegistry(self.assets, snapshot)
        _, expected = plan_chunks(
            snapshot,
            job.profile,
            job.first_frame,
            job.first_frame + job.duration_frames,
            max_frames=job.plan.max_chunk_frames,
        )
        if [(c.first_frame, c.frame_count) for c in expected] != [
            (c.first_frame, c.frame_count) for c in job.chunks
        ]:
            raise ValueError("chunk ranges differ from their frozen plan")
        return snapshot

    def _tools(self, job):
        capabilities = doctor(self.settings, self.store.root)
        if not capabilities.ready:
            raise ValueError("media tools/storage are not ready; run tabi doctor")
        if job.plan.toolchain_fingerprint not in {None, capabilities.fingerprint}:
            raise ValueError("media toolchain changed; create a new job")
        return capabilities.fingerprint

    def _owned_path(self, job, path):
        path = relative_path(path)
        if not path.startswith(f"jobs/artifacts/{job.id}/"):
            raise JobOwnershipError("artifact is outside this job's owned directory")
        return path

    def _verified_chunk(self, job, chunk):
        if (
            chunk.output is None
            or chunk.report_path is None
            or chunk.output.location.root_id != "project"
        ):
            raise ValueError("chunk has no verified owned artifact/report")
        relative = self._owned_path(job, chunk.output.location.path)
        report = self.store.read(self._owned_path(job, chunk.report_path))
        actual = self._artifact(relative)
        if actual != chunk.output or not isinstance(report, RenderReport):
            raise ValueError("chunk hash or report has changed")
        if (
            report.snapshot_sha256 != job.snapshot_sha256
            or report.first_frame != job.first_frame + chunk.first_frame
            or report.frame_count != chunk.frame_count
            or report.canvas != job.profile.canvas
            or report.fps != job.profile.fps
            or report.backend != job.backend
            or report.toolchain_fingerprint != job.plan.toolchain_fingerprint
            or (report.output_sha256, report.output_bytes) != (actual.sha256, actual.size_bytes)
            or not report.full_decode_passed
            or not report.timestamps_verified
            or report.audio_mix is not None
            or report.audio_verification is not None
        ):
            raise ValueError("chunk report is incompatible with this frozen job")
        verify_video(
            self.settings, self.store.root / relative, video_profile(job.profile), chunk.frame_count
        )
        return actual

    def resume(self, identity):
        with self.store.exclusive_lock(".tabi-worker.lock"):
            self._recover()
            job = self.ledger.get(identity)
            if job.state not in {"paused", "interrupted", "cancelled", "failed"}:
                raise ValueError("only paused, interrupted, cancelled or failed jobs can resume")
            self._validate_plan(job)
            fingerprint = self._tools(job)
            chunks, invalid = [], []
            for chunk in job.chunks:
                if chunk.state == "verified":
                    try:
                        self._verified_chunk(job, chunk)
                        chunks.append(chunk)
                        continue
                    except OperationCancelled:
                        raise
                    except (ValueError, OSError, ToolError) as error:
                        invalid.append(f"chunk {chunk.index}: {error}")
                chunks.append(
                    chunk.model_copy(
                        update={"state": "pending", "output": None, "report_path": None}
                    )
                )
            # Invalid or unfinished media stays as an old artifact. A new attempt
            # receives new paths, so no interrupted or verified file is overwritten.
            return self.ledger.update(
                identity,
                "resume_validated",
                lambda current: revised(
                    current,
                    state="queued",
                    owner=None,
                    cancel_requested=False,
                    plan=current.plan.model_copy(update={"toolchain_fingerprint": fingerprint}),
                    chunks=chunks,
                    completed_frames=sum(c.frame_count for c in chunks if c.state == "verified"),
                    output=None if invalid else current.output,
                    report_path=None if invalid else current.report_path,
                    error=JobError(code="chunk_invalidated", message="; ".join(invalid)[:4096])
                    if invalid
                    else None,
                ),
            )

    @staticmethod
    def _chunk_update(job, index, **changes):
        chunks = [
            chunk.model_copy(update=changes) if chunk.index == index else chunk
            for chunk in job.chunks
        ]
        return revised(
            job,
            chunks=chunks,
            completed_frames=sum(c.frame_count for c in chunks if c.state == "verified"),
        )

    def _execute(self, job):
        identity = job.id
        snapshot = self._validate_plan(job)
        fingerprint = self._tools(job)
        if job.plan.toolchain_fingerprint is None:
            job = self.ledger.update(
                identity,
                "toolchain_locked",
                lambda current: revised(
                    self._owned(current),
                    plan=current.plan.model_copy(update={"toolchain_fingerprint": fingerprint}),
                ),
            )
        estimate = estimate_storage(self.assets, job)
        if not estimate.sufficient:
            raise ValueError(
                f"insufficient project storage: estimate {estimate.required_additional_bytes} "
                f"additional bytes, {estimate.available_bytes} available; inspect/prune caches "
                "or free space before resuming"
            )
        registry = FrozenRegistry(self.assets, snapshot)
        cache = CacheStore(self.store)
        folder = f"jobs/artifacts/{identity}"
        with self.store._directory(self.store._parts(folder), create=True):
            pass
        for chunk in job.chunks:
            checkpoint(force=True)
            if chunk.state == "verified":
                try:
                    self._verified_chunk(job, chunk)
                    continue
                except OperationCancelled:
                    raise
                except (ValueError, OSError, ToolError):
                    pass
            index = chunk.index
            job = self.ledger.update(
                identity,
                "chunk_started",
                lambda current, index=index: self._chunk_update(
                    self._owned(current),
                    index,
                    state="rendering",
                    output=None,
                    report_path=None,
                ),
            )
            attempt = f"{folder}/chunk-{index:06}-{uuid4().hex}"
            chunk_path, report_path = f"{attempt}.mp4", f"{attempt}-report.json"
            first = job.first_frame + chunk.first_frame
            descriptor = video_descriptor(snapshot, registry, job, chunk)
            report = self._cached_chunk(cache, descriptor, job, chunk, chunk_path)
            if report is None:
                report = FFmpegRenderer(self.assets, self.settings).clip(
                    snapshot,
                    first,
                    first + chunk.frame_count,
                    self.store.root / chunk_path,
                    video_profile(job.profile),
                )
            if report.toolchain_fingerprint != fingerprint or report.backend != job.backend:
                raise ValueError("renderer/toolchain changed during chunk execution")
            self.store._atomic_write(report_path, canonical_bytes(report), overwrite=False)
            artifact = self._artifact(chunk_path)
            if (artifact.sha256, artifact.size_bytes) != (
                report.output_sha256,
                report.output_bytes,
            ):
                raise ValueError("chunk changed after verification")
            if report.cache_reuse is None:
                cache.put(
                    "video_chunk",
                    descriptor,
                    self.store.root / chunk_path,
                    report=report,
                    refresh=True,
                )
            job = self.ledger.update(
                identity,
                "chunk_verified",
                lambda current, index=index, artifact=artifact, report_path=report_path: (
                    self._chunk_update(
                        self._owned(current),
                        index,
                        state="verified",
                        output=artifact,
                        report_path=report_path,
                    )
                ),
            )
        # A crash after assembly can reuse that verified owned output as well.
        report = self._existing_assembly(job)
        if report is None:
            assembled = f"{folder}/assembly-{uuid4().hex}"
            report = VideoAssembler(self.assets, self.settings).render(
                snapshot,
                job,
                self.store.root / f"{assembled}.mp4",
                [
                    (self.store.root / c.output.location.path, c.frame_count, c.output.sha256)
                    for c in job.chunks
                ],
            )
            report_path = f"{assembled}-report.json"
            self.store._atomic_write(report_path, canonical_bytes(report), overwrite=False)
            artifact = self._artifact(f"{assembled}.mp4")
            job = self.ledger.update(
                identity,
                "assembly_verified",
                lambda current: revised(
                    self._owned(current),
                    output=artifact,
                    report_path=report_path,
                ),
            )
        checkpoint(force=True)
        FrozenRegistry(self.assets, snapshot)
        if job.plan.pipeline != pipeline_fingerprint() or report.backend != job.backend:
            raise ValueError(
                "render pipeline changed during execution; verified artifacts retained"
            )
        final_report = report.model_copy(update={"output": str(self.store.root / job.destination)})
        final_report_path = f"{folder}/final-{uuid4().hex}-report.json"
        self.store._atomic_write(final_report_path, canonical_bytes(final_report), overwrite=False)

        def finish(current):
            self._owned(current)
            if current.cancel_requested:
                raise OperationCancelled("job cancelled before final publication")
            try:
                self._publish(current.output.location.path, current.destination)
            except FileExistsError:
                existing = self._artifact(current.destination)
                if (existing.sha256, existing.size_bytes) != (
                    current.output.sha256,
                    current.output.size_bytes,
                ):
                    raise ValueError(
                        "existing export differs from this verified job; it was preserved"
                    ) from None
            return revised(
                current,
                state="verified",
                owner=None,
                report_path=final_report_path,
                output=current.output.model_copy(
                    update={"location": MediaPath(path=current.destination)}
                ),
            )

        return self.ledger.update(identity, "verified", finish)

    def _cached_chunk(self, cache, descriptor, job, chunk, path):
        started = time.monotonic()
        output = self.store.root / path
        entry = cache.lookup("video_chunk", descriptor, destination=output)
        if entry is None:
            return None
        previous = entry.report
        try:
            if (
                previous.purpose != descriptor["purpose"]
                or previous.first_frame != descriptor["first_frame"]
                or previous.frame_count != chunk.frame_count
                or previous.canvas != job.profile.canvas
                or previous.fps != job.profile.fps
                or previous.backend != job.backend
                or previous.toolchain_fingerprint != job.plan.toolchain_fingerprint
                or not previous.full_decode_passed
                or not previous.timestamps_verified
                or previous.audio_mix is not None
                or previous.audio_verification is not None
                or previous.assembly is not None
            ):
                raise ValueError("cached report is incompatible with this chunk")
            verify_video(self.settings, output, video_profile(job.profile), chunk.frame_count)
            return RenderReport.model_validate(
                {
                    **previous.model_dump(),
                    "snapshot_sha256": job.snapshot_sha256,
                    "output": str(output),
                    "render_seconds": time.monotonic() - started,
                    "normalized_images": 0,
                    "normalized_cache_hits": 0,
                    "cache_reuse": CacheReuse(
                        key=entry.key,
                        origin_snapshot_sha256=previous.snapshot_sha256,
                    ),
                }
            )
        except OperationCancelled:
            raise
        except (ValueError, OSError, ToolError):
            output.unlink(missing_ok=True)  # Only this new, independent job copy.
            return None

    def _existing_assembly(self, job):
        if job.output is None or job.report_path is None:
            return None
        try:
            path = self._owned_path(job, job.output.location.path)
            if self._artifact(path) != job.output:
                return None
            report = self.store.read(self._owned_path(job, job.report_path))
            if (
                not isinstance(report, RenderReport)
                or report.assembly is None
                or report.snapshot_sha256 != job.snapshot_sha256
                or report.first_frame != job.first_frame
                or report.frame_count != job.duration_frames
                or report.canvas != job.profile.canvas
                or report.fps != job.profile.fps
                or report.backend != job.backend
                or report.toolchain_fingerprint != job.plan.toolchain_fingerprint
                or report.output_sha256 != job.output.sha256
                or report.output_bytes != job.output.size_bytes
                or report.assembly.chunk_sha256 != [chunk.output.sha256 for chunk in job.chunks]
            ):
                return None
            verify_video(self.settings, self.store.root / path, job.profile, job.duration_frames)
            if job.profile.audio_codec:
                with tempfile.TemporaryDirectory(
                    prefix=".tabi-verify-", dir=self.store.root / "jobs"
                ) as scratch:
                    verify_aac(
                        self.settings,
                        self.store.root / path,
                        job.profile.fps.sample_at(job.first_frame + job.duration_frames)
                        - job.profile.fps.sample_at(job.first_frame),
                        Path(scratch),
                    )
            return report
        except OperationCancelled:
            raise
        except (ValueError, OSError, ToolError):
            return None

    def work(self, *, once=False):
        results = []
        with self.store.exclusive_lock(".tabi-worker.lock"):
            self._recover()
            while queued := [job for job in self.ledger.all() if job.state == "queued"]:
                results.append(self._run(queued[0].id))
                if once:
                    break
        return results

    def _artifact(self, relative):
        parts = self.store._parts(relative)
        digest = hashlib.sha256()
        with self.store._directory(parts[:-1]) as directory:
            descriptor = os.open(
                parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory
            )
            with os.fdopen(descriptor, "rb") as stream:
                if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                    raise ValueError("job artifact must be a regular file")
                for block in iter(lambda: stream.read(1024 * 1024), b""):
                    checkpoint()
                    digest.update(block)
                size = stream.tell()
        return HashedFile(
            location=MediaPath(path=relative), sha256=digest.hexdigest(), size_bytes=size
        )

    def _publish(self, source, destination):
        src, dst = self.store._parts(source), self.store._parts(destination)
        with (
            self.store._directory(src[:-1]) as source_dir,
            self.store._directory(dst[:-1], create=True) as destination_dir,
        ):
            os.link(
                src[-1],
                dst[-1],
                src_dir_fd=source_dir,
                dst_dir_fd=destination_dir,
                follow_symlinks=False,
            )
            os.fsync(destination_dir)

    def _run(self, identity):
        def claim(job):
            if job.state != "queued" or job.cancel_requested:
                raise JobOwnershipError("job is no longer queued")
            return revised(job, state="running", owner=self.owner, error=None)

        try:
            job = self.ledger.update(identity, "started", claim)
        except JobOwnershipError:
            return self.ledger.get(identity)
        try:
            with execution_scope(
                ExecutionScope(lambda: self._cancelled(identity), self.on_process)
            ):
                return self._execute(job)
        except KeyboardInterrupt:
            self.ledger.update(
                identity,
                "interrupted",
                lambda current: revised(
                    self._owned(current),
                    state="interrupted",
                    owner=None,
                    error=JobError(
                        code="worker_interrupted", message="Worker interrupted by the operator."
                    ),
                ),
            )
            raise
        except Exception as error:
            current = self.ledger.get(identity)
            if current.state == "verified":
                # The event committed but its convenience checkpoint failed.
                # Journal readers already see the verified artifact truthfully.
                return current
            cancelled = isinstance(error, OperationCancelled) or current.cancel_requested
            code = (
                "cancelled"
                if cancelled
                else "process_failed"
                if isinstance(error, ToolError)
                else "render_failed"
            )
            message = str(error).strip()[:4096] or type(error).__name__
            log_path = f"jobs/artifacts/{identity}/error-{current.revision:08}.log"
            self.store._atomic_write(log_path, message.encode("utf-8"), overwrite=False)
            return self.ledger.update(
                identity,
                "cancelled" if cancelled else "failed",
                lambda job: revised(
                    self._owned(job),
                    state="cancelled" if cancelled else "failed",
                    owner=None,
                    chunks=[
                        chunk.model_copy(update={"state": "pending" if cancelled else "failed"})
                        if chunk.state == "rendering"
                        else chunk
                        for chunk in job.chunks
                    ],
                    error=JobError(
                        code=code,
                        message=message,
                        log_path=log_path,
                    ),
                ),
            )
