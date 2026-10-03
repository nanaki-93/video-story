"""Reproducible, unpublished effects stress project; one isolated export per invocation."""

import argparse
import json
import math
import os
import platform
import resource
import shutil
import subprocess
import threading
import time
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
from PIL import Image

from tabi.core.assets import AssetService
from tabi.core.config import load_settings
from tabi.core.fixtures import generate_fixtures, hashed, write_wav
from tabi.core.jobs import JobService
from tabi.core.models import ActionPack, Asset, Episode, SceneTemplate
from tabi.core.models.base import canonical_bytes, content_hash
from tabi.core.persistence import ProjectStore
from tabi.core.process import run_tool
from tabi.core.render.ffmpeg import FFmpegRenderer
from tabi.core.render.profiles import ENCODERS, PRESETS, preset_profile
from tabi.core.timeline.compiler import ActionCompiler
from tabi.core.toolchain import doctor, file_hash


def scaled(mapping, factor, fields):
    if mapping:
        for name in fields:
            mapping[name] *= factor


def prepare(root, seconds, scale):
    manifest = generate_fixtures(root, profile="effects")
    store = ProjectStore(root)
    for path in sorted((root / "registry/assets").glob("*/*.json")):
        asset = store.read(path.relative_to(root).as_posix())
        data = asset.model_dump(mode="json")
        if asset.kind != "audio":
            for entry in data["files"]:
                image_path = root / entry["location"]["path"]
                with Image.open(image_path) as image:
                    image.resize(
                        (image.width * scale, image.height * scale), Image.Resampling.NEAREST
                    ).save(image_path)
                entry.update(sha256=file_hash(image_path), size_bytes=image_path.stat().st_size)
            scaled(data["probe"]["canvas"], scale, ("width", "height"))
            for key in ("anchor", "pivot"):
                scaled(data["compatibility"][key], scale, ("x", "y"))
            scaled(data["compatibility"]["crop"], scale, ("x", "y", "width", "height"))
        elif asset.id == "fixture.tone":
            source = root / asset.files[0].location.path
            write_wav(source, seconds * 48000)
            data["files"][0].update(sha256=file_hash(source), size_bytes=source.stat().st_size)
            data["probe"]["duration_samples"] = seconds * 48000
        store.save_draft(Asset.model_validate(data), expected_revision=asset.revision)
    template = store.read("registry/templates/scene.synthetic.train/1.0.json")
    data = template.model_dump(mode="json")
    scaled(data["design_canvas"], scale, ("width", "height"))
    for anchor in data["anchors"].values():
        scaled(anchor, scale, ("x", "y"))
    scaled(data["parameter_limits"]["travel_speed"], scale, ("minimum", "maximum"))
    for slot in data["slots"]:
        if slot["tile_period"]:
            slot["tile_period"] *= scale
    store.save_draft(SceneTemplate.model_validate(data), expected_revision=template.revision)
    pack = store.read("registry/actions/pack.synthetic/1.0.json")
    data = pack.model_dump(mode="json")
    scaled(data["canvas"], scale, ("width", "height"))
    scaled(data["anchor"], scale, ("x", "y"))
    store.save_draft(ActionPack.model_validate(data), expected_revision=pack.revision)
    episode = store.read("episodes/episode.synthetic.json")
    data = episode.model_dump(mode="json")
    count = seconds * 30
    data.update(title="SYNTHETIC export stress test", duration_frames=count)
    scaled(data["canvas"], scale, ("width", "height"))
    data["scenes"][0].update(end_frame=count, final_state=None)
    data["actions"] = [
        {
            **a,
            "id": f"{a['id']}-cycle{n}",
            "start_frame": a["start_frame"] + n * 300,
            "end_frame": a["end_frame"] + n * 300,
        }
        for n in range(seconds // 10)
        for a in data["actions"]
    ]
    data["events"] = [
        {
            **e,
            "id": f"{e['id']}-cycle{n}",
            "start_frame": n * 300,
            "end_frame": (n + 1) * 300,
            "world_x": (e["world_x"] + n * 780) * scale,
        }
        for n in range(seconds // 10)
        for e in data["events"]
    ]
    for curve in data["curves"]:
        factor = scale if curve["target"] == "travel_speed" else 1
        keys = {
            k["frame"] + n * 300: k["value"] * factor
            for n in range(seconds // 10)
            for k in curve["keys"]
        }
        curve["keys"] = [{"frame": frame, "value": value} for frame, value in sorted(keys.items())]
        scaled(curve["limits"], factor, ("minimum", "maximum"))
    data["tracks"][0]["trim_end_sample"] = seconds * 48000
    data["notes"] = (
        "Synthetic geometric stress workload with a newly generated full-duration triangle signal. "
        "Repeated authored test cycles exercise rain, reflection, lighting, landmarks, "
        "body transitions and depth layers; no approved Tabi art or original music is represented."
    )
    episode = store.save_draft(Episode.model_validate(data), expected_revision=episode.revision)
    # The manifest describes the transformed fixture, not its original ten-second scaffold.
    files = [
        hashed(root, p)
        for p in sorted(root.rglob("*"))
        if p.is_file() and p.name not in {"fixtures.json", ".tabi.lock"}
    ]
    manifest = manifest.model_copy(
        update={
            "files": files,
            "generator_sha256": content_hash(
                {"base": manifest.generator_sha256, "benchmark": file_hash(Path(__file__))}
            ),
        }
    )
    (root / "fixtures.json").write_bytes(canonical_bytes(manifest))
    assets = AssetService(store)
    snapshot = ActionCompiler(assets, purpose="synthetic_test").compile(episode)
    return assets, snapshot, store.save_snapshot(snapshot)


class ResidentSampler:
    """Sample only this Python process and its retained, live tool children."""

    def __init__(self):
        self.processes, self.observations = [], []
        self.stopped = threading.Event()
        self.thread = threading.Thread(target=self.sample, daemon=True)

    def sample(self):
        while not self.stopped.is_set():
            pids = [os.getpid(), *(p.pid for p in self.processes if p.poll() is None)]
            result = subprocess.run(
                ["ps", "-o", "rss=", "-p", ",".join(str(p) for p in pids)],
                capture_output=True,
                check=False,
                timeout=5,
            )
            if result.returncode == 0:
                self.observations.append(sum(int(n) for n in result.stdout.split()) * 1024)
            self.stopped.wait(0.25)


def quality(assets, settings, snapshot, profile, output, root):
    frames = sorted(
        {
            0,
            89,
            151,
            215,
            snapshot.episode.duration_frames // 2,
            snapshot.episode.duration_frames - 1,
        }
    )
    folder = root / "quality"
    folder.mkdir()
    select = "+".join(f"eq(n\\,{frame})" for frame in frames)
    run_tool(
        [
            settings.ffmpeg,
            "-v",
            "error",
            "-nostdin",
            "-n",
            "-i",
            str(output),
            "-an",
            "-vf",
            f"select={select},scale=in_color_matrix=bt709:in_range=tv:out_range=pc,format=rgb24",
            "-fps_mode",
            "passthrough",
            str(folder / "decoded-%02d.png"),
        ],
        timeout=3600,
    )
    checks = []
    for index, frame in enumerate(frames, 1):
        reference = folder / f"reference-{frame}.png"
        FFmpegRenderer(assets, settings).frame(snapshot, frame, reference, canvas=profile.canvas)
        decoded = folder / f"decoded-{index:02}.png"
        with Image.open(reference) as expected, Image.open(decoded) as actual:
            difference = np.asarray(actual).astype(np.float32) - np.asarray(expected)
            rms = float(np.sqrt(np.mean(difference**2)))
            absolute = np.abs(difference)
            mean, p99 = float(np.mean(absolute)), float(np.quantile(absolute, 0.99))
        checks.append(
            dict(
                frame=frame,
                mean_absolute_rgb_error=mean,
                p99_rgb_error=p99,
                psnr_db=20 * math.log10(255 / rms) if rms else None,
                within_test_tolerance=mean < 3 and p99 < 24,
                decoded=str(decoded),
                reference=str(reference),
            )
        )
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--preset", choices=PRESETS, required=True)
    parser.add_argument("--encoder", choices=ENCODERS, required=True)
    parser.add_argument("--seconds", type=int, default=60)
    parser.add_argument("--design-scale", type=int, choices=[1, 2, 3, 6], default=3)
    args = parser.parse_args()
    if args.seconds < 10 or args.seconds % 10:
        parser.error("duration must be a positive multiple of ten seconds")
    root = args.output_root.expanduser().resolve()
    assets, snapshot, digest = prepare(root, args.seconds, args.design_scale)
    settings = load_settings(args.config, env=os.environ, cwd=Path.cwd(), home=Path.home())
    capabilities = doctor(settings, root)
    profile = preset_profile(args.preset, fps=snapshot.episode.fps, encoder=args.encoder)
    sampler = ResidentSampler()
    service = JobService(assets, settings, on_process=sampler.processes.append)
    job = service.submit(digest, profile, "exports/stress.mp4")
    before_free = shutil.disk_usage(root).free
    before_cpu = [
        resource.getrusage(kind) for kind in (resource.RUSAGE_SELF, resource.RUSAGE_CHILDREN)
    ]
    started = time.monotonic()
    sampler.thread.start()
    try:
        result = service.work()[0]
    finally:
        sampler.stopped.set()
        sampler.thread.join(timeout=6)
    wall = time.monotonic() - started
    after_cpu = [
        resource.getrusage(kind) for kind in (resource.RUSAGE_SELF, resource.RUSAGE_CHILDREN)
    ]
    report = dict(
        observed_at=datetime.now(UTC).isoformat(),
        purpose="synthetic_test",
        machine=capabilities.machine.model_dump(mode="json"),
        toolchain_fingerprint=capabilities.fingerprint,
        ffmpeg=capabilities.ffmpeg.version,
        profile=profile.model_dump(mode="json"),
        source_canvas=snapshot.episode.canvas.model_dump(),
        workload=snapshot.episode.notes,
        job_id=job.id,
        snapshot_sha256=digest,
        state=result.state,
        error=result.error.model_dump() if result.error else None,
        wall_seconds=wall,
        rendered_frames=result.completed_frames,
        effective_frames_per_second=result.completed_frames / wall,
        cpu_seconds=sum(
            (a.ru_utime + a.ru_stime) - (b.ru_utime + b.ru_stime)
            for a, b in zip(after_cpu, before_cpu, strict=True)
        ),
        sampled_process_rss_peak_bytes=max(sampler.observations, default=0),
        rss_samples=len(sampler.observations),
        rss_interval_seconds=0.25,
        worker_peak_rss_bytes=after_cpu[0].ru_maxrss
        * (1 if platform.system() == "Darwin" else 1024),
        largest_child_peak_rss_bytes=after_cpu[1].ru_maxrss
        * (1 if platform.system() == "Darwin" else 1024),
        memory_scope="Worker and retained live tools; sampled RSS excludes other apps, kernel "
        "and unreported GPU allocations. rusage peaks are per process, not summed.",
        free_disk_before_bytes=before_free,
        free_disk_after_bytes=shutil.disk_usage(root).free,
        output=result.output.model_dump(mode="json") if result.output else None,
        chunk_reports=[
            assets.store.read(c.report_path).model_dump(mode="json")
            for c in result.chunks
            if c.report_path
        ],
    )
    report_path = root / "benchmark.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    if result.state != "verified":
        raise RuntimeError(f"benchmark failed; inspect {report_path}: {result.error}")
    report["verification"] = service.verify_export(job.id).model_dump(mode="json")
    report["quality"] = quality(
        assets, settings, snapshot, profile, root / result.destination, root
    )
    report["all_quality_checks_pass"] = all(q["within_test_tolerance"] for q in report["quality"])
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    print(
        json.dumps(
            {
                key: report[key]
                for key in (
                    "wall_seconds",
                    "effective_frames_per_second",
                    "sampled_process_rss_peak_bytes",
                    "all_quality_checks_pass",
                )
            },
            indent=2,
        )
    )
    print(report_path)
    if not sampler.observations or not report["all_quality_checks_pass"]:
        raise SystemExit("benchmark evidence failed its memory-observation or quality gate")


if __name__ == "__main__":
    main()
