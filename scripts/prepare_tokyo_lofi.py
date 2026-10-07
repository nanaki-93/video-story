"""L05: conform supplied Tokyo artwork into a reusable, silent 90-second pilot.

Generation is intentionally separate: --generated must contain reviewed window-mask.png,
closed-eyes.png and foliage.png, plus the preparation/prompt evidence. No network,
model downloads, automatic approvals, or writes to the original artwork occur here.
Use a NEW --output directory for each version. FFmpeg performs media conforming;
the normal Python services own the scene, timeline, preview, and verified export.
"""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
from dataclasses import replace
from pathlib import Path

import numpy as np
from PIL import Image

from tabi.core.assets import AssetService
from tabi.core.config import load_settings
from tabi.core.jobs import JobService
from tabi.core.lofi import LofiService
from tabi.core.models import Episode
from tabi.core.models.base import AssetRef, FrameRate
from tabi.core.models.lofi import CreateLofiVideo, LofiScene
from tabi.core.models.registry import ImportRequest
from tabi.core.persistence import ProjectStore
from tabi.core.render.ffmpeg import FFmpegRenderer
from tabi.core.render.profiles import preset_profile
from tabi.core.timeline.compiler import ActionCompiler

WIDTH, HEIGHT, FPS, SECONDS = 1664, 936, 30, 90
PANEL, OVERLAP = 1856, 240
ORDER = [
    "04-yanaka-residential-rooftops-panorama.png",
    "01-asakusa-sensoji-panorama.png",
    "02-sumida-river-skytree-panorama.png",
    "03-ueno-shinobazu-pond-panorama.png",
    "05-shinjuku-skyline-panorama.png",
    "06-tokyo-bay-rainbow-bridge-panorama.png",
]


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def settings_for(output):
    settings = load_settings(None, env=os.environ, cwd=Path.cwd(), home=Path.home())
    return replace(settings, cache_root=output / "cache", project_root=output / "projects")


def run_ffmpeg(settings, arguments):
    subprocess.run(
        [settings.ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin", "-n", *arguments],
        check=True,
    )


def conform(settings, source, destination, filters):
    run_ffmpeg(
        settings,
        ["-i", str(source), "-vf", filters, "-frames:v", "1", "-update", "1", str(destination)],
    )


def prepare(args):
    output = args.output.resolve()
    # Never mutate an existing prepared version or approved project.
    output.mkdir(parents=True, exist_ok=False)
    settings = settings_for(output)
    project = output / "projects" / "Tabi Tokyo Sunset"
    store = ProjectStore.initialize(project, "Tabi · Tokyo sunset · silent asset pilot")
    sources = project / "sources" / "prepared"
    sources.mkdir(parents=True)
    evidence = output / "evidence"
    evidence.mkdir()
    raw = args.generated.resolve()
    artwork = args.artwork.resolve()
    originals = [artwork / "tabi-train-example.png"]
    originals += [artwork / "tokyo-scenario" / name for name in ORDER]
    originals += [raw / "window-mask.png", raw / "closed-eyes.png", raw / "foliage.png"]
    hashes = {str(path): digest(path) for path in originals}
    write_json(evidence / "source-hashes.json", hashes)
    for source in [
        raw.parent / "preparation.json",
        raw / "mask-correction-prompt.txt",
        raw / "foliage-prompt.txt",
    ]:
        shutil.copy2(source, evidence / source.name)
    master = sources / "master.png"
    shutil.copy2(originals[0], master)
    with Image.open(master) as image:
        if image.size != (WIDTH, HEIGHT):
            raise ValueError("this preparation is calibrated to the original 1664×936 master")

    # Restrict the generated matte to measured glass regions, protecting the
    # hanging handles/walls. Correct two small false gill-shaped islands in glass.
    mask = sources / "window.png"
    conform(
        settings,
        raw / "window-mask.png",
        mask,
        f"scale={WIDTH}:{HEIGHT}:flags=lanczos,format=gray,"
        "lut=y='if(gte(val,128),255,0)',"
        "geq=lum='if(gte(X,738),if(lt(Y,325)*gte(X,744),255,lum(X,Y)),"
        "if((between(X,0,30)*between(Y,111,333)*"
        "not(between(Y,156,174)+between(Y,190,203)))+"
        "(between(X,97,136)*between(Y,76,360))+"
        "(between(X,170,217)*between(Y,47,365)),lum(X,Y),0))',format=gray",
    )
    closed = sources / "closed-eyes-aligned.png"
    conform(settings, raw / "closed-eyes.png", closed, f"scale={WIDTH}:{HEIGHT}:flags=lanczos")
    # Tiny feathered eye regions only. Generated changes elsewhere never reach the scene.
    left = "clip((1-pow((X-609)/46,2)-pow((Y-383)/34,2))*8,0,1)"
    right = "clip((1-pow((X-715)/21,2)-pow((Y-375)/29,2))*8,0,1)"
    patch = sources / "closed-eyes-overlay.png"
    conform(
        settings,
        closed,
        patch,
        f"format=rgba,geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='255*max({left},{right})'",
    )
    blink_dir = sources / "blink"
    blink_dir.mkdir()
    # A 0.3-second closed-eye blink; transparency restores the untouched master.
    opacity = [0, 0.55, 1, 1, 1, 1, 1, 0.55, 0]
    frames = []
    for index, alpha in enumerate(opacity):
        target = blink_dir / f"frame-{index:04}.png"
        conform(settings, patch, target, f"format=rgba,colorchannelmixer=aa={alpha}")
        frames.append(target)

    # Six independently supplied districts become ONE periodic spatial strip.
    # Blend the previous panel's tail into each panel's head, including last→first.
    # No time cuts or whole-scene crossfades are introduced by the renderer.
    panels, pieces = [], []
    for index, source in enumerate(originals[1:7]):
        panel = sources / f"panel-{index:02}.png"
        conform(
            settings,
            source,
            panel,
            f"scale=-2:720:flags=lanczos,crop={PANEL}:720,"
            f"pad={PANEL}:{HEIGHT}:0:0:color=0x735462,format=rgb24",
        )
        panels.append(panel)
    for index, panel in enumerate(panels):
        piece = sources / f"district-{index:02}.png"
        graph = (
            f"[0:v]crop={OVERLAP}:{HEIGHT}:{PANEL - OVERLAP}:0[tail];"
            "[1:v]split[headsrc][bodysrc];"
            f"[headsrc]crop={OVERLAP}:{HEIGHT}:0:0[head];"
            f"[bodysrc]crop={PANEL - 2 * OVERLAP}:{HEIGHT}:{OVERLAP}:0[body];"
            "[tail][head]blend=all_expr='A*(1-X/W)+B*X/W'[join];"
            "[join][body]hstack=inputs=2,format=rgb24[out]"
        )
        run_ffmpeg(
            settings,
            [
                "-i",
                str(panels[index - 1]),
                "-i",
                str(panel),
                "-filter_complex",
                graph,
                "-map",
                "[out]",
                "-frames:v",
                "1",
                "-update",
                "1",
                str(piece),
            ],
        )
        pieces.append(piece)
    period = len(panels) * (PANEL - OVERLAP)
    strip = sources / "tokyo-six-districts.png"
    foliage = sources / "foliage-join.png"
    conform(
        settings,
        raw / "foliage.png",
        foliage,
        "scale=-2:720:flags=lanczos,crop=720:720,format=rgba,"
        "geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':"
        "a='alpha(X,Y)*min(clip(X/120,0,1),clip((W-1-X)/120,0,1))'",
    )
    inputs = [part for piece in pieces for part in ["-i", str(piece)]]
    inputs += ["-i", str(foliage)]
    labels = "".join(f"[{index}:v]" for index in range(len(pieces)))
    graph = f"{labels}hstack=inputs={len(pieces)}[base0];"
    graph += f"[6:v]split=7{''.join(f'[foliage{i}]' for i in range(7))};"
    for index in range(7):
        x = index * (PANEL - OVERLAP) - 240
        graph += f"[base{index}][foliage{index}]overlay=x={x}:y=0:format=rgb[base{index + 1}];"
    graph += (
        "[base7]split[whole][opening];"
        f"[opening]crop={WIDTH}:{HEIGHT}:0:0[guard];"
        "[whole][guard]hstack=inputs=2,format=rgb24[out]"
    )
    run_ffmpeg(
        settings,
        [
            *inputs,
            "-filter_complex",
            graph,
            "-map",
            "[out]",
            "-frames:v",
            "1",
            "-update",
            "1",
            str(strip),
        ],
    )

    assets = AssetService(store, ffmpeg=settings.ffmpeg, ffprobe=settings.ffprobe)
    fps = FrameRate(num=FPS, den=1)

    def register(name, files, kind="still", generated=False):
        assets.import_asset(
            ImportRequest(
                id=f"tokyo.pilot.{name}",
                version="1.0",
                kind=kind,
                paths=[{"path": str(path.relative_to(project))} for path in files],
                fps=fps if kind == "sequence" else None,
                provenance={
                    "origin": "generated" if generated else "user_supplied",
                    "commercial_use": "pending",
                    "notes": (
                        "L05 local draft; preparation and exact source hashes in sibling evidence. "
                        "No publication or hash-bound creative approval asserted."
                    ),
                    "generation": {
                        "model_name": "OpenAI built-in imagegen (revision not exposed)",
                        "notes": "2026-10-08; reviewed hosted output terms; source rights pending",
                    }
                    if generated
                    else None,
                },
            )
        )
        return AssetRef(id=f"tokyo.pilot.{name}", version="1.0")

    scene = LofiScene(
        schema_version="1.0",
        id="tokyo.sunset",
        title="Tokyo sunset · six districts",
        master=register("master", [master]),
        fps=fps,
        window_mask=register("window", [mask], "mask", True),
        scenery=[
            {
                "id": "tokyo",
                "asset": register("scenery", [strip], generated=True),
                "repeat_width": period,
            }
        ],
        speed=period / SECONDS,
        overlays=[
            {
                "id": "blink",
                "asset": register("blink", frames, "sequence", True),
                "timing": {
                    "source": {"start_frame": 0, "end_frame": len(frames)},
                    "repeat_frames": 225,
                    "first_frame": 78,
                },
            }
        ],
        notes=(
            "Original Tabi master; generated closed-eye patch; six supplied Tokyo panoramas. "
            "90-second panorama cycle, blink every 7.5s; no music/audio. "
            "Foliage softens spatial joins; all panes share the panorama. "
            "Visual and rights acceptance remain pending."
        ),
    )
    service = LofiService(assets)
    scene = service.save(scene, expected_revision=None)
    episode = service.create_video(
        CreateLofiVideo(
            id="tokyo.silent.90s",
            title="Tabi in Tokyo · silent 90-second loop",
            scene=AssetRef(id=scene.id, version=scene.version),
            expected_scene_revision=scene.revision,
            duration_seconds=SECONDS,
            music=[],
        )
    )
    snapshot = ActionCompiler(assets, purpose="preview").compile(episode)
    snapshot_hash = store.save_snapshot(snapshot)
    with Image.open(strip) as image:
        assert image.size == (period + WIDTH, HEIGHT)
        assert (
            image.crop((0, 0, WIDTH, HEIGHT)).tobytes()
            == image.crop((period, 0, period + WIDTH, HEIGHT)).tobytes()
        )
    with Image.open(patch) as image:
        alpha = np.asarray(image)[:, :, 3]
        assert not alpha[:340].any() and not alpha[418:].any()
        assert not alpha[:, :562].any() and not alpha[:, 737:].any()
    assert not snapshot.audio_placements
    assert all(digest(path) == value for path, value in hashes.items())
    manifest = {
        "task": "L05",
        "project": str(project),
        "snapshot_sha256": snapshot_hash,
        "episode": episode.id,
        "scene": scene.id,
        "duration_frames": FPS * SECONDS,
        "fps": {"num": FPS, "den": 1},
        "canvas": {"width": WIDTH, "height": HEIGHT},
        "audio": "none",
        "district_order": ORDER,
        "strip_period": period,
        "speed_pixels_per_second": period / SECONDS,
        "blink_period_frames": 225,
        "original_files_unchanged": True,
        "source_sha256": hashes,
        "prepared_files": {
            str(path.relative_to(project)): digest(path) for path in sorted(sources.rglob("*.png"))
        },
        "status": "prepared; visual review and export pending",
    }
    write_json(output / "manifest.json", manifest)
    print(json.dumps({"prepared": str(output), "snapshot": snapshot_hash}), flush=True)


def review(args):
    output = args.output.resolve()
    manifest = json.loads((output / "manifest.json").read_text())
    store = ProjectStore(Path(manifest["project"]))
    settings = settings_for(output)
    assets = AssetService(store, ffmpeg=settings.ffmpeg, ffprobe=settings.ffprobe)
    snapshot = store.read_snapshot(manifest["snapshot_sha256"])
    renderer = FFmpegRenderer(assets, settings)
    frames = output / "review"
    frames.mkdir(exist_ok=True)
    for frame in args.frames:
        path = frames / f"frame-{frame:04}.png"
        if not path.exists():
            renderer.frame(snapshot, frame, path)
        print(str(path), flush=True)


def render(args):
    output = args.output.resolve()
    manifest = json.loads((output / "manifest.json").read_text())
    store = ProjectStore(Path(manifest["project"]))
    settings = settings_for(output)
    assets = AssetService(store, ffmpeg=settings.ffmpeg, ffprobe=settings.ffprobe)
    service = JobService(assets, settings)
    profile = preset_profile(args.profile).model_copy(update={"audio_codec": None})
    job = service.submit(
        manifest["snapshot_sha256"],
        profile,
        f"exports/Tabi-Tokyo-90s-Silent-{args.profile}-DRAFT.mp4",
        max_chunk_frames=450,
    )
    print(json.dumps({"job": job.id, "output": job.destination}), flush=True)
    service.work(once=True)
    verification = service.verify_export(job.id)
    write_json(output / f"verification-{args.profile}.json", verification.model_dump(mode="json"))
    print(verification.model_dump_json(indent=2), flush=True)


def verify(args):
    """Check a real prepared project without converting technical checks into approval."""
    output = args.output.resolve()
    manifest = json.loads((output / "manifest.json").read_text())
    store = ProjectStore(Path(manifest["project"]))
    settings = settings_for(output)
    assets = AssetService(store, ffmpeg=settings.ffmpeg, ffprobe=settings.ffprobe)
    snapshot = store.read_snapshot(manifest["snapshot_sha256"])
    sources = store.root / "sources" / "prepared"
    with Image.open(sources / "window.png") as image:
        stable = np.asarray(image) == 0
    with Image.open(sources / "closed-eyes-overlay.png") as image:
        stable &= np.asarray(image)[:, :, 3] == 0
    stable[-28:] = False  # Deliberate draft-preview badge.
    review_paths = sorted((output / "review").glob("frame-*.png"))
    if not review_paths:
        raise ValueError("run review first")
    with Image.open(output / "review" / "frame-0000.png") as image:
        opening = np.asarray(image.convert("RGB")).astype(np.int16)
    stable_delta = 0
    for path in review_paths:
        with Image.open(path) as image:
            pixels = np.asarray(image.convert("RGB")).astype(np.int16)
        stable_delta = max(stable_delta, int(np.abs(pixels - opening)[stable].max()))
    assert stable_delta == 0, "fixed artwork changes outside the window/eyelids"

    # Inspect the mathematically next frame after the delivered loop. Use a new
    # in-memory preview episode; do not alter the saved 90-second version.
    data = snapshot.episode.model_dump(mode="json")
    data["duration_frames"] += 1
    data["scenes"][-1]["end_frame"] += 1
    data["scenes"][-1]["final_state"] = None
    extended = ActionCompiler(assets, purpose="preview").compile(Episode.model_validate(data))
    loop_frame = output / "evidence" / "loop-next-frame.png"
    if not loop_frame.exists():
        FFmpegRenderer(assets, settings).frame(extended, FPS * SECONDS, loop_frame)
    with Image.open(loop_frame) as image:
        pixels = np.asarray(image.convert("RGB")).astype(np.int16)
    loop_delta = int(np.abs(pixels - opening).max())
    assert loop_delta == 0, "90-second scene does not return exactly to its opening state"
    originals_unchanged = all(
        digest(Path(path)) == value for path, value in manifest["source_sha256"].items()
    )
    assert originals_unchanged
    verification = json.loads((output / f"verification-{args.profile}.json").read_text())
    video = store.root / verification["output"]["location"]["path"]
    probe = json.loads(
        subprocess.check_output(
            [
                settings.ffprobe,
                "-v",
                "error",
                "-show_streams",
                "-show_format",
                "-of",
                "json",
                str(video),
            ]
        )
    )
    assert len(probe["streams"]) == 1 and probe["streams"][0]["codec_type"] == "video"
    assert int(probe["streams"][0]["nb_frames"]) == FPS * SECONDS
    assert float(probe["format"]["duration"]) == SECONDS
    contact = output / "review" / "full-video-contact.jpg"
    if not contact.exists():
        run_ffmpeg(
            settings,
            [
                "-i",
                str(video),
                "-vf",
                "fps=1/5,scale=384:216,tile=6x3",
                "-frames:v",
                "1",
                "-update",
                "1",
                "-q:v",
                "2",
                str(contact),
            ],
        )
    result = {
        "source_files_unchanged": originals_unchanged,
        "reviewed_frame_count": len(review_paths),
        "fixed_region_pixel_count": int(stable.sum()),
        "fixed_region_max_channel_delta": stable_delta,
        "loop_next_frame_vs_opening_max_channel_delta": loop_delta,
        "audio_stream_count": 0,
        "duration_seconds": float(probe["format"]["duration"]),
        "video_frame_count": int(probe["streams"][0]["nb_frames"]),
        "output_sha256": digest(video),
        "technical_export_verification": verification,
        "visual_acceptance": "pending Marco review; numeric checks do not approve artwork",
    }
    write_json(output / "quality-checks.json", result)
    print(json.dumps(result, indent=2), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["prepare", "review", "render", "verify"])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--artwork", type=Path, default=Path("docs/assets/scenario"))
    parser.add_argument("--generated", type=Path)
    parser.add_argument("--profile", choices=["proxy", "1080p"], default="1080p")
    parser.add_argument(
        "--frames", nargs="+", type=int, default=[0, 80, 300, 450, 900, 1350, 1800, 2250, 2699]
    )
    args = parser.parse_args()
    if args.command == "prepare" and args.generated is None:
        parser.error("prepare requires --generated (the reviewed imagegen output folder)")
    {"prepare": prepare, "review": review, "render": render, "verify": verify}[args.command](args)


if __name__ == "__main__":
    main()
