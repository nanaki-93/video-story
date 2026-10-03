"""Launch and control only our child, verified over private readiness and HTTP."""

import json
import os
import secrets
import select
import signal
import socket
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from urllib.request import Request, urlopen

from .contracts import PROTOCOL, WorkerReady


def validate_ready(payload, *, pid, port, nonce):
    ready = WorkerReady.model_validate_json(payload)
    if (ready.pid, ready.port) != (pid, port) or not secrets.compare_digest(ready.nonce, nonce):
        raise ValueError("worker readiness does not match the owned process/socket")
    return ready


class OwnedWorker:
    def __init__(self, settings, roots, web_root, *, timeout=20, session_lifetime=43200):
        self.process = None
        self.ready = None
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        read_fd, write_fd = os.pipe()
        try:
            listener.bind(("127.0.0.1", 0))
            listener.listen(128)
            self.port = listener.getsockname()[1]
            self.origin = f"http://127.0.0.1:{self.port}"
            nonce = secrets.token_urlsafe(32)
            self.process = subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "tabi.api.worker",
                    "--socket-fd",
                    str(listener.fileno()),
                    "--ready-fd",
                    str(write_fd),
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                pass_fds=(listener.fileno(), write_fd),
                start_new_session=True,
            )
            os.close(write_fd)
            write_fd = -1
            payload = {
                "protocol": PROTOCOL,
                "nonce": nonce,
                "settings": settings.as_dict(),
                "roots": {key: str(path) for key, path in roots.items()},
                "web_root": str(web_root),
                "session_lifetime": session_lifetime,
            }
            self.process.stdin.write(json.dumps(payload).encode() + b"\n")
            self.process.stdin.close()
            received, deadline = b"", time.monotonic() + timeout
            while b"\n" not in received:
                remaining = deadline - time.monotonic()
                if remaining <= 0 or not select.select([read_fd], [], [], remaining)[0]:
                    raise ValueError("local worker readiness timed out")
                block = os.read(read_fd, 65537 - len(received))
                if not block or len(received) + len(block) > 65536:
                    raise ValueError("local worker failed before a valid readiness message")
                received += block
            self.ready = validate_ready(received, pid=self.process.pid, port=self.port, nonce=nonce)
            session = self.request("GET", "/api/v1/session")
            if (session["protocol"], session["session_id"], session["pid"]) != (
                PROTOCOL,
                self.ready.session_id,
                self.process.pid,
            ):
                raise ValueError("owned worker HTTP handshake did not match readiness")
        except BaseException:
            if self.process and self.process.poll() is None:
                # Startup failed before any projects were opened. Signal only this Popen child.
                self.process.terminate()
                try:
                    self.process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait()
            if self.process and self.process.stderr:
                self.process.stderr.close()
            raise ValueError("local worker failed readiness/protocol validation") from None
        finally:
            listener.close()
            os.close(read_fd)
            if write_fd >= 0:
                os.close(write_fd)

    def request(self, method, path, body=None):
        if self.process.poll() is not None:
            raise ValueError("the owned local worker has stopped")
        headers = {"Authorization": f"Bearer {self.ready.bearer}"}
        data = None
        if method not in {"GET", "HEAD"}:
            headers["Content-Type"] = "application/json"
            data = json.dumps(body if body is not None else {}).encode()
        request = Request(self.origin + path, data=data, method=method, headers=headers)
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read(16 * 1024 * 1024 + 1))

    def browser_url(self, *, fresh=False):
        secret = (
            self.request("POST", "/api/v1/bootstrap-ticket")["secret"]
            if fresh
            else self.ready.bootstrap
        )
        return f"{self.origin}/#bootstrap={secret}"

    def stop(self, *, cancel=True, timeout=45):
        if self.process.poll() is None:
            self.request("POST", "/api/v1/shutdown", {"mode": "cancel" if cancel else "after_job"})
            self.process.wait(timeout=timeout)
        if self.process.stderr:
            self.process.stderr.close()


def default_web_root():
    bundled = Path(__file__).resolve().parents[1] / "web"
    if (bundled / "index.html").is_file():
        return bundled
    checkout = Path(__file__).resolve().parents[3] / "web/dist"
    if (checkout / "index.html").is_file():
        return checkout
    raise ValueError("Built frontend missing; run make web-build or install the packaged app")


def launch(settings, roots, *, web_root=None, no_open=False):
    worker = OwnedWorker(settings, roots, web_root or default_web_root())
    previous_handlers = {}

    def interrupted(signum, frame):
        raise KeyboardInterrupt

    for signum in (signal.SIGTERM, signal.SIGHUP):
        previous_handlers[signum] = signal.signal(signum, interrupted)
    # This public URL deliberately omits the one-time fragment and all session secrets.
    print(
        json.dumps({"url": worker.origin, "pid": worker.process.pid, "protocol": PROTOCOL}),
        flush=True,
    )
    interactive = sys.stdin.isatty()
    if interactive:
        print(
            "Enter 'open' to reopen, or 'stop' to stop after the current job. "
            "Ctrl-C cancels owned work.",
            flush=True,
        )
    try:
        if not no_open:
            webbrowser.open(worker.browser_url())
        while worker.process.poll() is None:
            if interactive and select.select([sys.stdin], [], [], 0.25)[0]:
                line = sys.stdin.readline()
                command = line.strip()
                if command == "open":
                    webbrowser.open(worker.browser_url(fresh=True))
                elif command == "stop":
                    worker.request("POST", "/api/v1/shutdown", {"mode": "after_job"})
                elif not line:
                    interactive = False
            else:
                time.sleep(0.1)
    except KeyboardInterrupt:
        worker.stop(cancel=True)
    finally:
        if worker.process.poll() is None:
            worker.stop(cancel=True)
        if worker.process.stderr:
            worker.process.stderr.close()
        for signum, handler in previous_handlers.items():
            signal.signal(signum, handler)
    return worker.process.returncode
