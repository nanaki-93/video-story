"""T25 synthetic-only browser spike. T26 owns the authenticated production service.

Serves one explicitly selected verified synthetic job and its renderer stills.
No folder browsing, uploads, editing, credentials or arbitrary-file routes exist.
"""

import argparse
import json
import mimetypes
import os
import re
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

from tabi.core.assets import AssetService
from tabi.core.config import load_settings
from tabi.core.jobs import JobService
from tabi.core.models.base import Canvas, canonical_bytes
from tabi.core.persistence import ProjectStore
from tabi.core.render.ffmpeg import FFmpegRenderer


def byte_range(header, size):
    if not header:
        return 0, size
    match = re.fullmatch(r"bytes=(\d*)-(\d*)", header)
    if not match or not any(match.groups()):
        raise ValueError("unsupported range")
    first, last = match.groups()
    if first:
        start, end = int(first), min(size, int(last) + 1) if last else size
    else:
        start, end = max(0, size - int(last)), size
    if not 0 <= start < end <= size:
        raise ValueError("unsatisfied range")
    return start, end


def serve(project, settings, job_id, web_root, *, port=0):
    assets = AssetService(ProjectStore(project), ffmpeg=settings.ffmpeg, ffprobe=settings.ffprobe)
    service = JobService(assets, settings)
    job = service.ledger.get(job_id)
    snapshot = assets.store.read_snapshot(job.snapshot_sha256)
    if (
        snapshot.purpose != "synthetic_test"
        or job.first_frame != 0
        or job.duration_frames != snapshot.episode.duration_frames
        or job.duration_frames > 1800
        or not job.profile.audio_codec
    ):
        raise ValueError(
            "spike accepts only a complete synthetic H.264/AAC job of at most 1800 frames"
        )
    verification = service.verify_export(job_id)
    encoded = canonical_bytes(verification)
    video = assets.store.root / job.destination
    original_stat = video.stat()
    web_root = web_root.resolve(strict=True)
    if not (web_root / "index.html").is_file():
        raise ValueError("build web/ before running the browser spike")
    renderer = FFmpegRenderer(assets, settings)
    lock = threading.Lock()
    with tempfile.TemporaryDirectory(prefix=".tabi-browser-spike-") as temporary:
        frames = Path(temporary)
        reports = {}

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, *args):
                pass  # No request URLs, file paths or browser data in logs.

            def do_GET(self):
                self.respond()

            def do_HEAD(self):
                self.respond(head=True)

            def end_headers(self):
                self.send_header("Cache-Control", "no-store")
                self.send_header("X-Content-Type-Options", "nosniff")
                self.send_header("Referrer-Policy", "no-referrer")
                self.send_header(
                    "Content-Security-Policy",
                    (
                        "default-src 'self'; script-src 'self'; style-src 'self'; "
                        "img-src 'self' blob: data:; media-src 'self' blob:; "
                        "object-src 'none'; base-uri 'none'; frame-ancestors 'none'"
                    ),
                )
                super().end_headers()

            def respond(self, *, head=False):
                host = f"127.0.0.1:{self.server.server_port}"
                if self.headers.get("Host") != host or self.headers.get("Origin") not in {
                    None,
                    f"http://{host}",
                }:
                    self.send_error(403)
                    return
                parts = urlsplit(self.path)
                route = unquote(parts.path)
                if parts.query or ".." in route.split("/") or "\\" in route:
                    self.send_error(400)
                    return
                try:
                    if route == "/spike/export.json":
                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.send_header("Content-Length", str(len(encoded)))
                        self.end_headers()
                        if not head:
                            self.wfile.write(encoded)
                        return
                    if route == "/spike/video.mp4":
                        current = video.stat()
                        if (
                            current.st_dev,
                            current.st_ino,
                            current.st_size,
                            current.st_mtime_ns,
                        ) != (
                            original_stat.st_dev,
                            original_stat.st_ino,
                            original_stat.st_size,
                            original_stat.st_mtime_ns,
                        ):
                            self.send_error(409, "Registered video changed")
                            return
                        path = video
                    elif match := re.fullmatch(r"/spike/frame/(\d+)\.(png|json)", route):
                        frame, suffix = int(match[1]), match[2]
                        if not 0 <= frame < job.duration_frames:
                            self.send_error(400)
                            return
                        with lock:
                            if frame not in reports:
                                output = frames / f"{frame}.png"
                                report = renderer.frame(
                                    snapshot, frame, output, canvas=Canvas(width=960, height=540)
                                )
                                (frames / f"{frame}.json").write_bytes(canonical_bytes(report))
                                reports[frame] = report
                            path = frames / f"{frame}.{suffix}"
                    else:
                        path = (web_root / (route.lstrip("/") or "index.html")).resolve()
                        if not path.is_relative_to(web_root) or not path.is_file():
                            self.send_error(404)
                            return
                    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
                    with os.fdopen(descriptor, "rb") as stream:
                        size = os.fstat(stream.fileno()).st_size
                        try:
                            first, end = byte_range(self.headers.get("Range"), size)
                        except ValueError:
                            self.send_response(416)
                            self.send_header("Content-Range", f"bytes */{size}")
                            self.send_header("Content-Length", "0")
                            self.end_headers()
                            return
                        partial = self.headers.get("Range") is not None
                        self.send_response(206 if partial else 200)
                        self.send_header(
                            "Content-Type",
                            mimetypes.guess_type(path)[0] or "application/octet-stream",
                        )
                        self.send_header("Accept-Ranges", "bytes")
                        self.send_header("Content-Length", str(end - first))
                        if partial:
                            self.send_header("Content-Range", f"bytes {first}-{end - 1}/{size}")
                        self.end_headers()
                        if not head:
                            stream.seek(first)
                            remaining = end - first
                            while remaining:
                                block = stream.read(min(65536, remaining))
                                if not block:
                                    break
                                self.wfile.write(block)
                                remaining -= len(block)
                except (BrokenPipeError, ConnectionResetError):
                    pass
                except (OSError, ValueError):
                    self.send_error(500, "Synthetic fixture unavailable")

        server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
        print(
            json.dumps(
                {
                    "url": f"http://127.0.0.1:{server.server_port}",
                    "purpose": "synthetic_test",
                    "job_id": job.id,
                }
            ),
            flush=True,
        )
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--job", required=True)
    parser.add_argument("--config", type=Path)
    parser.add_argument(
        "--web-root", type=Path, default=Path(__file__).resolve().parents[1] / "web/dist"
    )
    args = parser.parse_args()
    serve(
        args.project,
        load_settings(args.config, env=os.environ, cwd=Path.cwd(), home=Path.home()),
        args.job,
        args.web_root,
    )
