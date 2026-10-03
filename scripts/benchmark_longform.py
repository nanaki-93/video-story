"""Owned 45–60 minute synthetic reliability run, crash/recovery and every chunk boundary."""

import argparse
import json
import math
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
from benchmark_exports import prepare
from PIL import Image

from tabi.core.assets import AssetService
from tabi.core.config import load_settings
from tabi.core.jobs import JobService
from tabi.core.jobs.planner import pipeline_fingerprint
from tabi.core.persistence import ProjectStore
from tabi.core.process import run_tool
from tabi.core.render.ffmpeg import FFmpegRenderer
from tabi.core.render.profiles import preset_profile
from tabi.core.toolchain import doctor


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


class Sampler:
    """Disk-backed samples and a bounded list of retained, live Popen handles."""

    def __init__(self, root, service, identity, phase):
        self.root, self.service, self.identity = root, service, identity
        self.handles = {}
        self.lock = threading.Lock()
        self.stop = threading.Event()
        self.started = time.monotonic()
        self.path = root / f"resources-{phase}.jsonl"
        self.thread = threading.Thread(target=self.sample, daemon=True)

    def observe(self, process):
        with self.lock:
            self.handles = {pid: p for pid, p in self.handles.items() if p.poll() is None}
            self.handles[process.pid] = process

    def sample(self):
        last_progress, storage = -1, {}
        with self.path.open("x", buffering=1) as log:
            while not self.stop.is_set():
                with self.lock:
                    self.handles = {pid: p for pid, p in self.handles.items() if p.poll() is None}
                    pids = [os.getpid(), *self.handles]
                try:
                    result = subprocess.run(
                        ["ps", "-o", "pid=,rss=", "-p", ",".join(map(str, pids))],
                        capture_output=True,
                        check=True,
                        text=True,
                        timeout=5,
                    )
                    rss = {
                        int(p): int(size) * 1024
                        for p, size in (line.split() for line in result.stdout.splitlines())
                    }
                    job = self.service.ledger.get(self.identity)
                    if job.completed_frames != last_progress:
                        sizes, allocated, seen = 0, 0, set()
                        for path in self.root.rglob("*"):
                            try:
                                if path.is_file() and not path.is_symlink():
                                    info = path.stat()
                                    sizes += info.st_size
                                    if (info.st_dev, info.st_ino) not in seen:
                                        allocated += info.st_blocks * 512
                                        seen.add((info.st_dev, info.st_ino))
                            except FileNotFoundError:
                                pass  # An owned render temporary was just retired.
                        storage = {
                            "logical_project_bytes": sizes,
                            "allocated_project_bytes": allocated,
                            "project_inodes": len(seen),
                        }
                        last_progress = job.completed_frames
                        print(
                            json.dumps(
                                {
                                    "phase": self.path.stem,
                                    "state": job.state,
                                    "frames": job.completed_frames,
                                    "total": job.duration_frames,
                                }
                            ),
                            flush=True,
                        )
                    sample = {
                        "seconds": time.monotonic() - self.started,
                        "state": job.state,
                        "frames": job.completed_frames,
                        "python_rss_bytes": rss.pop(os.getpid(), 0),
                        "tools_rss_bytes": sum(rss.values()),
                        "live_tools": len(rss),
                        "python_open_fds": len(os.listdir("/dev/fd")),
                        **storage,
                    }
                    log.write(json.dumps(sample) + "\n")
                except (OSError, ValueError, subprocess.SubprocessError) as error:
                    log.write(
                        json.dumps(
                            {"error": str(error), "seconds": time.monotonic() - self.started}
                        )
                        + "\n"
                    )
                self.stop.wait(1)


def worker(args, settings):
    assets = AssetService(ProjectStore(args.output_root))
    receipt = json.loads((args.output_root / "run.json").read_text())
    service = JobService(assets, settings)
    sampler = Sampler(args.output_root, service, receipt["job_id"], args.worker)
    service.on_process = sampler.observe

    def interrupted(signum, frame):
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, interrupted)
    sampler.thread.start()
    try:
        if args.worker == "crash":
            original = service.ledger.update

            def crash_at_boundary(identity, kind, transform):
                result = original(identity, kind, transform)
                if kind == "chunk_started" and result.completed_frames >= 1774:
                    # The prior owned subprocess has exited. Crash after committing
                    # the next chunk-start event but before spawning another tool.
                    with sampler.lock:
                        assert not any(p.poll() is None for p in sampler.handles.values())
                    write_json(
                        args.output_root / "retained-before-crash.json",
                        {
                            "chunks": [
                                c.model_dump(mode="json")
                                for c in result.chunks
                                if c.state == "verified"
                            ],
                            "frames": result.completed_frames,
                        },
                    )
                    print("Injected owned worker exit at a committed chunk boundary", flush=True)
                    os._exit(23)
                return result

            service.ledger.update = crash_at_boundary
        else:
            service.recover()
            service.resume(receipt["job_id"])
        result = service.work(once=True)[0]
        write_json(args.output_root / f"result-{args.worker}.json", result.model_dump(mode="json"))
        if result.state != "verified":
            raise RuntimeError(str(result.error))
    finally:
        sampler.stop.set()
        sampler.thread.join(timeout=8)


def frame_selection(frames):
    # A flat sum of hundreds of eq() terms exceeds libavutil's parser depth.
    # Explicitly balance the expression; selection still uses exact decoded n.
    terms = [f"eq(n\\,{frame})" for frame in frames]
    while len(terms) > 1:
        terms = [
            f"({terms[i]}+{terms[i + 1]})" if i + 1 < len(terms) else terms[i]
            for i in range(0, len(terms), 2)
        ]
    return terms[0]


def boundary_quality(assets, settings, snapshot, job):
    root = assets.store.root
    folder = Path(tempfile.mkdtemp(prefix="boundary-review-", dir=root))
    frames = sorted(
        {
            0,
            job.duration_frames - 1,
            *[n for c in job.chunks[1:] for n in (c.first_frame - 1, c.first_frame)],
        }
    )
    select = frame_selection(frames)
    run_tool(
        [
            settings.ffmpeg,
            "-v",
            "error",
            "-nostdin",
            "-n",
            "-i",
            str(root / job.destination),
            "-an",
            "-vf",
            f"select={select},scale=in_color_matrix=bt709:in_range=tv:out_range=pc,format=rgb24",
            "-fps_mode",
            "passthrough",
            str(folder / "decoded-%04d.png"),
        ],
        timeout=3600,
    )
    checks = []
    for index, frame in enumerate(frames, 1):
        reference = folder / f"reference-{frame:06}.png"
        FFmpegRenderer(assets, settings).frame(
            snapshot, frame, reference, canvas=job.profile.canvas
        )
        decoded = folder / f"decoded-{index:04}.png"
        with Image.open(reference) as expected, Image.open(decoded) as actual:
            difference = np.asarray(actual).astype(np.float32) - np.asarray(expected)
            absolute = np.abs(difference)
            mean, p99 = float(np.mean(absolute)), float(np.quantile(absolute, 0.99))
            rms = float(np.sqrt(np.mean(difference**2)))
        checks.append(
            {
                "frame": frame,
                "mean_absolute_rgb_error": mean,
                "p99_rgb_error": p99,
                "psnr_db": 20 * math.log10(255 / rms) if rms else None,
                "pass": mean < 3 and p99 < 24,
                "decoded": decoded.relative_to(root).as_posix(),
                "reference": reference.relative_to(root).as_posix(),
            }
        )
        write_json(root / "boundary-checks.json", checks)
        if index % 20 == 0:
            print(f"Verified {index}/{len(frames)} boundary reference frames", flush=True)
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--seconds", type=int, default=2700)
    parser.add_argument("--design-scale", type=int, choices=[1, 3], default=3)
    parser.add_argument(
        "--encoder", choices=["libx264", "h264_videotoolbox"], default="h264_videotoolbox"
    )
    parser.add_argument("--worker", choices=["crash", "resume"])
    parser.add_argument(
        "--review-existing", action="store_true", help="Recheck an already verified owned run"
    )
    args = parser.parse_args()
    args.output_root = args.output_root.resolve()
    settings = load_settings(args.config, env=os.environ, cwd=Path.cwd(), home=Path.home())
    if args.worker:
        return worker(args, settings)
    if args.review_existing:
        return review_existing(args, settings)
    if not 2700 <= args.seconds <= 3600 or args.seconds % 10:
        parser.error("use a complete 45–60 minute Session in whole ten-second cycles")
    print("Preparing owned full-duration synthetic fixture", flush=True)
    assets, snapshot, digest = prepare(args.output_root, args.seconds, args.design_scale)
    service = JobService(assets, settings)
    profile = preset_profile("1080p", fps=snapshot.episode.fps, encoder=args.encoder)
    job = service.submit(digest, profile, "exports/session.mp4", max_chunk_frames=887)
    capabilities = doctor(settings, args.output_root)
    write_json(
        args.output_root / "run.json",
        {
            "job_id": job.id,
            "snapshot_sha256": digest,
            "purpose": "synthetic_test",
            "seconds": args.seconds,
            "source_canvas": snapshot.episode.canvas.model_dump(),
            "machine": capabilities.machine.model_dump(mode="json"),
            "toolchain_fingerprint": capabilities.fingerprint,
            "profile": profile.model_dump(mode="json"),
        },
    )
    start, free_before = time.monotonic(), shutil.disk_usage(args.output_root).free
    for phase in ("crash", "resume"):
        process = subprocess.Popen(
            [
                sys.executable,
                str(Path(__file__).resolve()),
                "--output-root",
                str(args.output_root),
                "--config",
                str(args.config.resolve()),
                "--worker",
                phase,
            ]
        )
        try:
            code = process.wait()
        except BaseException:
            process.terminate()
            process.wait(timeout=15)
            raise
        if code != (23 if phase == "crash" else 0):
            raise RuntimeError(f"owned {phase} worker failed with {code}; evidence preserved")
    wall = time.monotonic() - start
    job = service.ledger.get(job.id)
    write_json(
        args.output_root / "render-timing.json",
        {
            "wall_seconds": wall,
            "source": "Parent monotonic clock around the owned crash and resume workers",
            "free_disk_before_bytes": free_before,
        },
    )
    return finish_review(args.output_root, assets, settings, snapshot, service, job)


def review_existing(args, settings):
    root = args.output_root
    receipt = json.loads((root / "run.json").read_text())
    assets = AssetService(ProjectStore(root))
    service = JobService(assets, settings)
    job = service.ledger.get(receipt["job_id"])
    if job.state != "verified" or job.plan.pipeline != pipeline_fingerprint():
        raise ValueError("review needs a verified export and the unchanged core pipeline")
    if not (root / "render-timing.json").exists():
        events = service.ledger.events(job.id)
        began = next(event.recorded_at for event in events if event.kind == "started")
        ended = next(event.recorded_at for event in reversed(events) if event.kind == "verified")
        write_json(
            root / "render-timing.json",
            {
                "wall_seconds": (ended - began).total_seconds(),
                "source": (
                    "Recovered from durable first started / final verified UTC events; "
                    "includes crash/recovery but excludes parent startup before first started."
                ),
                "free_disk_before_bytes": None,
            },
        )
    return finish_review(
        root, assets, settings, assets.store.read_snapshot(job.snapshot_sha256), service, job
    )


def finish_review(root, assets, settings, snapshot, service, job):
    timing = json.loads((root / "render-timing.json").read_text())
    wall = timing["wall_seconds"]
    retained = json.loads((root / "retained-before-crash.json").read_text())
    unchanged = all(job.chunks[c["index"]].model_dump(mode="json") == c for c in retained["chunks"])
    print("Full render completed; checking final export and every chunk boundary", flush=True)
    verification = service.verify_export(job.id)
    checks = boundary_quality(assets, settings, snapshot, job)
    samples = [
        json.loads(line)
        for p in sorted(root.glob("resources-*.jsonl"))
        for line in p.read_text().splitlines()
    ]
    valid = [s for s in samples if "error" not in s]
    steady = [
        s for s in valid if 1774 <= s["frames"] < job.duration_frames - 887 and s["live_tools"]
    ]
    thirds = [part.tolist() for part in np.array_split(np.array(steady, dtype=object), 3)]
    report = {
        "observed_at": datetime.now(UTC).isoformat(),
        "run": json.loads((root / "run.json").read_text()),
        "state": job.state,
        "render_wall_seconds_including_recovery": wall,
        "render_timing_source": timing["source"],
        "frames_per_second_including_recovery": job.duration_frames / wall,
        "chunk_count": len(job.chunks),
        "retained_frames": retained["frames"],
        "retained_chunks_unchanged": unchanged,
        "output": job.output.model_dump(mode="json"),
        "verification": verification.model_dump(mode="json"),
        "all_boundary_checks_pass": all(c["pass"] for c in checks),
        "boundary_checks": len(checks),
        "sample_count": len(valid),
        "sampling_errors": [s for s in samples if "error" in s],
        "maximum_live_owned_tools": max(s["live_tools"] for s in valid),
        "maximum_python_open_fds": max(s["python_open_fds"] for s in valid),
        "peak_combined_rss_bytes": max(s["python_rss_bytes"] + s["tools_rss_bytes"] for s in valid),
        "steady_thirds": [
            {
                "samples": len(part),
                "python_median_rss_bytes": float(np.median([s["python_rss_bytes"] for s in part])),
                "tools_peak_rss_bytes": max(s["tools_rss_bytes"] for s in part),
            }
            for part in thirds
        ],
        "free_disk_before_bytes": timing["free_disk_before_bytes"],
        "free_disk_after_bytes": shutil.disk_usage(root).free,
        "memory_scope": (
            "Owned worker plus retained live media tools at 1-second intervals. "
            "Excludes other apps, kernel and unreported GPU memory. Samples stream to disk. "
            "Fixture preparation and post-render boundary review are outside render timing."
        ),
    }
    write_json(root / "longform-report.json", report)
    print(
        json.dumps(
            {
                k: report[k]
                for k in (
                    "state",
                    "render_wall_seconds_including_recovery",
                    "peak_combined_rss_bytes",
                    "all_boundary_checks_pass",
                    "retained_chunks_unchanged",
                )
            }
        ),
        flush=True,
    )
    if (
        not unchanged
        or not report["all_boundary_checks_pass"]
        or report["maximum_live_owned_tools"] > 1
        or report["sampling_errors"]
    ):
        raise SystemExit("long-form evidence failed; inspect retained report")


if __name__ == "__main__":
    main()
