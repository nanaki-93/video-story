"""Append-only, hash-linked job events with rebuildable atomic checkpoints."""

import os
import re
import stat
import threading
import time
from collections import OrderedDict
from contextlib import contextmanager
from dataclasses import dataclass
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


@dataclass(frozen=True)
class JournalTail:
    signatures: tuple
    event: JobEvent
    sha256: str
    created_at: datetime
    elapsed: float
    began: datetime | None


class JobLedger:
    def __init__(self, store):
        self.store = store
        # Keep one typed job per recently observed journal, never every historical
        # full chunk list. File metadata is rechecked on every read; changed history
        # forces a full hash-chain replay. Disk checkpoints remain untrusted caches.
        self._tails = OrderedDict()
        self._tail_lock = threading.RLock()

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

    @staticmethod
    def _signature(directory, name):
        info = os.stat(name, dir_fd=directory, follow_symlinks=False)
        if not stat.S_ISREG(info.st_mode):
            raise StorageError("job journal event is not a regular file")
        return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)

    def _tail(self, identity):
        identity = job_id(identity)
        with self._tail_lock, self.store._directory(("jobs", ".journals", identity)) as directory:
            names = sorted(
                name for name in os.listdir(directory) if re.fullmatch(r"\d{8}\.json", name)
            )
            if not names:
                raise FileNotFoundError("job has no committed journal events")
            if any(name != f"{i:08}.json" for i, name in enumerate(names)):
                raise StorageError("job journal has a missing event")
            signatures = tuple(self._signature(directory, name) for name in names)
            tail = self._tails.get(identity)
            if tail and len(signatures) < len(tail.signatures):
                raise StorageError("job journal has lost committed events")
            if tail and signatures[: len(tail.signatures)] != tail.signatures:
                tail = None
            start = len(tail.signatures) if tail else 0
            previous = tail.sha256 if tail else None
            elapsed, began = (tail.elapsed, tail.began) if tail else (0.0, None)
            created_at = tail.created_at if tail else None
            for sequence in range(start, len(names)):
                event = parse_document(self.store._read_at(directory, names[sequence]))
                if self._signature(directory, names[sequence]) != signatures[sequence]:
                    raise StorageError("job journal changed while being read")
                if not isinstance(event, JobEvent):
                    raise StorageError("journal contains a different document type")
                if (event.sequence, event.job.id, event.previous_sha256) != (
                    sequence,
                    identity,
                    previous,
                ):
                    raise StorageError("job journal identity or hash chain is invalid")
                if created_at is None:
                    created_at = event.recorded_at
                if event.job.state == "running" and began is None:
                    began = event.recorded_at
                elif event.job.state != "running" and began is not None:
                    elapsed += (event.recorded_at - began).total_seconds()
                    began = None
                previous = content_hash(event)
                tail = JournalTail(signatures, event, previous, created_at, elapsed, began)
            self._tails[identity] = tail
            self._tails.move_to_end(identity)
            while len(self._tails) > 8:
                self._tails.popitem(last=False)
            return tail

    def get(self, identity):
        return self._tail(identity).event.job.model_copy(deep=True)

    def timing(self, identity):
        tail = self._tail(identity)
        return tail.event.job.model_copy(deep=True), tail.elapsed, tail.began

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
                records.append(self._tail(identity))
            except FileNotFoundError:
                try:
                    self.store._read_bytes(f"jobs/{identity}.json")
                except FileNotFoundError:
                    # An interrupted first event may leave only an empty directory.
                    continue
                raise StorageError("an existing job has lost its journal") from None
        records.sort(key=lambda tail: (tail.created_at, tail.event.job.id))
        return [tail.event.job.model_copy(deep=True) for tail in records]

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
            previous = self._tail(identity).event
            updated = RenderJob.model_validate(transform(previous.job.model_copy(deep=True)))
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
