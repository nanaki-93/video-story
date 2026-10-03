"""One owned render lane shared by all browser tabs and opened projects."""

import threading
from dataclasses import dataclass

from fastapi import HTTPException

from tabi.core.assets import AssetService
from tabi.core.jobs import JobService
from tabi.core.models.base import content_hash
from tabi.core.persistence import ProjectBusy, ProjectStore

from .contracts import WebProject, WebProjects
from .files import Artifacts, RootRegistry
from .security import Sessions


@dataclass
class OpenProject:
    handle: str
    root_id: str
    path: str
    assets: AssetService
    jobs: JobService

    def info(self):
        return WebProject(
            schema_version="1.0",
            handle=self.handle,
            root_id=self.root_id,
            path=self.path,
            project=self.assets.store.read(),
        )


class Runtime:
    def __init__(self, settings, roots, *, sessions=None):
        self.settings = settings
        self.roots = RootRegistry(roots)
        self.sessions = sessions or Sessions()
        self.artifacts = Artifacts()
        self.projects = {}
        self.lock = threading.RLock()
        self.wake = threading.Event()
        self.stopping = threading.Event()
        self.cancelling = threading.Event()
        self.thread = None
        self.active = None
        self.failure = None
        self.on_stopped = lambda: None

    def open(self, root_id, path):
        folder = self.roots.directory(root_id, path)
        handle = "project-" + content_hash({"root": str(folder)})[:32]
        with self.lock:
            if handle in self.projects:
                return self.projects[handle]
            store = ProjectStore(folder)
            if store.root != folder:
                raise ValueError("project folder changed during opening")
            assets = AssetService(
                store,
                roots=self.roots.roots,
                ffmpeg=self.settings.ffmpeg,
                ffprobe=self.settings.ffprobe,
            )
            jobs = JobService(assets, self.settings)
            jobs.on_process = lambda process: self._cancel_if_stopping(jobs)
            try:
                jobs.recover()
            except ProjectBusy:
                pass  # Another genuine lease may own this project; never adopt it.
            result = OpenProject(handle, root_id, path, assets, jobs)
            self.projects[handle] = result
            self.wake.set()
            return result

    def get(self, handle):
        with self.lock:
            item = self.projects.get(handle)
        if item is None:
            raise HTTPException(404, "Project is not open in this worker")
        if self.roots.directory(item.root_id, item.path) != item.assets.store.root:
            raise ValueError("registered project folder changed")
        return item

    def listing(self):
        with self.lock:
            items = list(self.projects.values())
        return WebProjects(schema_version="1.0", projects=[item.info() for item in items])

    def start(self):
        self.thread = threading.Thread(
            target=self._work, name="tabi-owned-render-lane", daemon=True
        )
        self.thread.start()

    def _work(self):
        try:
            while not self.stopping.is_set():
                self.wake.wait(0.5)
                self.wake.clear()
                with self.lock:
                    items = list(self.projects.values())
                for item in items:
                    if self.stopping.is_set():
                        break
                    try:
                        if not any(job.state == "queued" for job in item.jobs.ledger.all()):
                            continue
                        with self.lock:
                            if self.stopping.is_set():
                                break
                            self.active = item
                        item.jobs.work(once=True)
                    except ProjectBusy:
                        pass
                    except Exception:
                        # Details remain in the job ledger; never leak request secrets in logs.
                        self.failure = "Queue could not read this project; inspect its job ledger"
                    finally:
                        with self.lock:
                            self.active = None
        finally:
            self.on_stopped()

    def stop(self, *, cancel=False):
        with self.lock:
            if cancel:
                self.cancelling.set()
            self.stopping.set()
            self.wake.set()
            if cancel and self.active:
                service = self.active.jobs
                for job in service.ledger.all():
                    if job.state == "running" and job.owner == service.owner:
                        service.cancel(job.id)

    def _cancel_if_stopping(self, service):
        # Covers shutdown between selecting a queued job and its first subprocess.
        if self.cancelling.is_set():
            for job in service.ledger.all():
                if job.state == "running" and job.owner == service.owner:
                    service.cancel(job.id)

    def cancel(self, item, identity):
        job = item.jobs.ledger.get(identity)
        if job.state == "running" and job.owner != item.jobs.owner:
            raise HTTPException(409, "Another worker owns this job; cancel it from its owner")
        return item.jobs.cancel(identity)
