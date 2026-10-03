"""Append-only, hash-linked job events with rebuildable atomic checkpoints."""

import os
import re
import time
from contextlib import contextmanager
from datetime import UTC, datetime

from pydantic import TypeAdapter

from ..documents import parse_document
from ..models.base import Identifier, canonical_bytes, content_hash
from ..models.production import JobEvent, RenderJob
from ..persistence import ProjectBusy, StorageError


def job_id(value):
    return TypeAdapter(Identifier).validate_python(value)


def revised(job, **changes):
    return RenderJob.model_validate({**job.model_dump(), **changes})


class JobLedger:
    def __init__(self, store):
        self.store = store

    @contextmanager
    def transaction(self):
        # Readers and cancellation requests share short project transactions;
        # the long-lived worker lease is deliberately a different inode.
        deadline = time.monotonic() + 3
        while True:
            lock = self.store.writer_lock()
            try:
                lock.__enter__()
                break
            except ProjectBusy:
                if time.monotonic() >= deadline:
                    raise
                time.sleep(0.01)
        try:
            yield
        finally:
            lock.__exit__(None, None, None)

    def events(self, identity):
        identity = job_id(identity)
        parts = ("jobs", ".journals", identity)
        with self.store._directory(parts) as directory:
            names = sorted(
                name for name in os.listdir(directory) if re.fullmatch(r"\d{8}\.json", name)
            )
            if not names:
                raise FileNotFoundError("job has no committed journal events")
            records, previous = [], None
            for sequence, name in enumerate(names):
                if name != f"{sequence:08}.json":
                    raise StorageError("job journal has a missing event")
                event = parse_document(self.store._read_at(directory, name))
                if not isinstance(event, JobEvent):
                    raise StorageError("journal contains a different document type")
                if (event.sequence, event.job.id, event.previous_sha256) != (
                    sequence,
                    identity,
                    previous,
                ):
                    raise StorageError("job journal identity or hash chain is invalid")
                records.append(event)
                previous = content_hash(event)
            return records

    def get(self, identity):
        return self.events(identity)[-1].job

    def all(self):
        try:
            with self.store._directory(("jobs", ".journals")) as directory:
                identities = [
                    job_id(name) for name in os.listdir(directory) if not name.startswith(".")
                ]
        except FileNotFoundError:
            return []
        records = []
        for identity in identities:
            try:
                records.append(self.events(identity))
            except FileNotFoundError:
                try:
                    self.store._read_bytes(f"jobs/{identity}.json")
                except FileNotFoundError:
                    # An interrupted first event may leave only an empty directory.
                    continue
                raise StorageError("an existing job has lost its journal") from None
        records.sort(key=lambda events: (events[0].recorded_at, events[0].job.id))
        return [events[-1].job for events in records]

    def _append(self, job, kind, previous):
        event = JobEvent(
            schema_version="1.0",
            sequence=job.revision,
            previous_sha256=content_hash(previous) if previous else None,
            recorded_at=datetime.now(UTC),
            kind=kind,
            job=job,
        )
        # The event is the commit point. A crash before checkpoint publication
        # cannot lose it: reads and recovery replay the journal.
        self.store._atomic_write(
            f"jobs/.journals/{job.id}/{job.revision:08}.json",
            canonical_bytes(event),
            overwrite=False,
        )
        self.store._atomic_write(f"jobs/{job.id}.json", canonical_bytes(job), overwrite=True)
        return job

    def create(self, job):
        job = RenderJob.model_validate(job)
        if job.revision != 0 or job.state != "queued":
            raise StorageError("new jobs must be queued at revision zero")
        with self.transaction():
            try:
                self.store._read_bytes(f"jobs/{job.id}.json")
            except FileNotFoundError:
                pass
            else:
                raise StorageError("job identity already exists")
            return self._append(job, "queued", None)

    def update(self, identity, kind, transform):
        with self.transaction():
            previous = self.events(identity)[-1]
            updated = RenderJob.model_validate(transform(previous.job))
            if updated.id != previous.job.id or updated.revision != previous.job.revision:
                raise StorageError("job updates cannot change identity or their input revision")
            if updated == previous.job:
                return updated
            return self._append(revised(updated, revision=updated.revision + 1), kind, previous)

    def checkpoint(self, identity):
        with self.transaction():
            job = self.get(identity)
            self.store._atomic_write(f"jobs/{job.id}.json", canonical_bytes(job), overwrite=True)
        return job
