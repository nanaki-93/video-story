"""Single-worker durable queue, owned execution and verified artifact publication."""

import hashlib
import os
import stat
from pathlib import Path
from uuid import uuid4

from ..models.base import HashedFile, MediaPath, canonical_bytes, relative_path
from ..models.production import ChunkRecord, JobError, OutputProfile, RenderJob
from ..process import ExecutionScope, OperationCancelled, ToolError, checkpoint, execution_scope
from ..render.backend import FrozenRegistry, backend_fingerprint
from ..render.ffmpeg import FFmpegRenderer
from .ledger import JobLedger, revised


class JobOwnershipError(ValueError):
    pass


class JobService:
    def __init__(self, assets, settings, *, on_process=None):
        self.assets, self.store, self.settings = assets, assets.store, settings
        self.ledger = JobLedger(self.store)
        self.owner = f"worker-{uuid4().hex}"
        self.on_process = on_process

    def submit(self, digest, profile, destination, *, first_frame=0, end_frame=None):
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
        if end - first_frame > 7200:
            raise ValueError("this bounded job needs the long-form chunk planner")
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
            chunks=[
                ChunkRecord(index=0, first_frame=0, frame_count=end - first_frame, state="pending")
            ],
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
                if job.backend != backend_fingerprint():
                    raise ValueError("renderer changed since submission; create a new job")
                snapshot = self.store.read_snapshot(job.snapshot_sha256)
                FrozenRegistry(self.assets, snapshot)
                folder = f"jobs/artifacts/{identity}"
                with self.store._directory(self.store._parts(folder), create=True):
                    pass
                job = self.ledger.update(
                    identity,
                    "chunk_started",
                    lambda current: revised(
                        self._owned(current),
                        chunks=[current.chunks[0].model_copy(update={"state": "rendering"})],
                    ),
                )
                chunk_path, report_path = (
                    f"{folder}/chunk-000000.mp4",
                    f"{folder}/chunk-000000-report.json",
                )
                report = FFmpegRenderer(self.assets, self.settings).clip(
                    snapshot,
                    job.first_frame,
                    job.first_frame + job.duration_frames,
                    self.store.root / chunk_path,
                    job.profile,
                )
                # The backend atomically publishes media only after a full decode.
                # A verified chunk and its report precede the ledger commit.
                self.store._atomic_write(report_path, canonical_bytes(report), overwrite=False)
                artifact = self._artifact(chunk_path)
                if (artifact.sha256, artifact.size_bytes) != (
                    report.output_sha256,
                    report.output_bytes,
                ):
                    raise ValueError("chunk changed after verification")
                job = self.ledger.update(
                    identity,
                    "chunk_verified",
                    lambda current: revised(
                        self._owned(current),
                        completed_frames=current.duration_frames,
                        chunks=[
                            current.chunks[0].model_copy(
                                update={
                                    "state": "verified",
                                    "output": artifact,
                                    "report_path": report_path,
                                }
                            )
                        ],
                    ),
                )
                checkpoint(force=True)
                final_report = report.model_copy(
                    update={"output": str(self.store.root / job.destination)}
                )
                final_report_path = f"{folder}/final-report.json"
                self.store._atomic_write(
                    final_report_path, canonical_bytes(final_report), overwrite=False
                )

                # Serialize the final cancellation check, publication and ledger completion.
                # A request after this point sees an already verified job.
                def finish(current):
                    self._owned(current)
                    if current.cancel_requested:
                        raise OperationCancelled("job cancelled before final publication")
                    self._publish(chunk_path, current.destination)
                    return revised(
                        current,
                        state="verified",
                        owner=None,
                        report_path=final_report_path,
                        output=artifact.model_copy(
                            update={"location": MediaPath(path=current.destination)}
                        ),
                    )

                return self.ledger.update(identity, "verified", finish)
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
