"""Durable queue commands; all execution and ownership remain in the core."""

import json

from tabi.core.assets import AssetService
from tabi.core.jobs import JobService
from tabi.core.models.base import Canvas
from tabi.core.models.production import OutputProfile
from tabi.core.persistence import ProjectStore

from .assets import trusted_roots
from .episodes import project_arguments


def add_job_commands(commands):
    parser = commands.add_parser("jobs", help="Submit, run, inspect or cancel durable local jobs")
    actions = parser.add_subparsers(dest="job_command", required=True)
    for name in ("submit", "list", "status", "events", "cancel", "recover", "work"):
        action = actions.add_parser(name)
        project_arguments(action)
        action.add_argument("--json", action="store_true", help="JSON is the default output format")
        if name in {"status", "events", "cancel"}:
            action.add_argument("job_id")
        if name == "work":
            action.add_argument("--once", action="store_true", help="Run at most one queued job")
        if name == "submit":
            action.add_argument("snapshot")
            action.add_argument("--output", required=True, help="New path under project exports/")
            action.add_argument("--start", type=int, default=0)
            action.add_argument("--end", type=int)
            action.add_argument("--width", type=int, default=960)
            action.add_argument("--height", type=int, default=540)
            action.add_argument(
                "--encoder", choices=["libx264", "h264_videotoolbox"], default="libx264"
            )
            action.add_argument("--audio-gain-db", type=float, default=0)


def run_job_command(args, settings):
    assets = AssetService(
        ProjectStore(args.project),
        roots=trusted_roots(args.root),
        ffmpeg=settings.ffmpeg,
        ffprobe=settings.ffprobe,
    )
    service = JobService(assets, settings)
    name = args.job_command
    if name == "submit":
        snapshot = assets.store.read_snapshot(args.snapshot)
        profile = OutputProfile(
            id="queued-preview",
            canvas=Canvas(width=args.width, height=args.height),
            fps=snapshot.episode.fps,
            container="mp4",
            video_codec=args.encoder,
            pixel_format="yuv420p",
            color_space="bt709",
            audio_codec="aac",
            audio_gain_db=args.audio_gain_db,
        )
        result = service.submit(
            args.snapshot,
            profile,
            args.output,
            first_frame=args.start,
            end_frame=args.end,
        )
    elif name == "list":
        result = service.ledger.all()
    elif name == "status":
        result = service.ledger.get(args.job_id)
    elif name == "events":
        result = service.ledger.events(args.job_id)
    elif name == "cancel":
        result = service.cancel(args.job_id)
    elif name == "recover":
        result = service.recover()
    else:
        result = service.work(once=args.once)
    print(
        json.dumps(
            [item.model_dump(mode="json") for item in result]
            if isinstance(result, list)
            else result.model_dump(mode="json"),
            ensure_ascii=False,
            indent=2,
        )
    )
    if name == "work":
        if any(job.state in {"failed", "interrupted"} for job in result):
            return 4
        if any(job.state == "cancelled" for job in result):
            return 5
    return 0
