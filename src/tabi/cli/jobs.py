"""Durable queue commands; all execution and ownership remain in the core."""

import json

from tabi.core.assets import AssetService
from tabi.core.cache.storage import estimate_storage
from tabi.core.jobs import JobService
from tabi.core.models.base import Canvas
from tabi.core.models.production import OutputProfile
from tabi.core.persistence import ProjectStore
from tabi.core.render.profiles import PRESETS, preset_profile

from .assets import trusted_roots
from .episodes import project_arguments


def add_job_commands(commands):
    parser = commands.add_parser("jobs", help="Submit, run, inspect or cancel durable local jobs")
    actions = parser.add_subparsers(dest="job_command", required=True)
    for name in (
        "submit",
        "list",
        "status",
        "events",
        "cancel",
        "pause",
        "resume",
        "recover",
        "work",
        "estimate",
        "verify",
    ):
        action = actions.add_parser(name)
        project_arguments(action)
        action.add_argument("--json", action="store_true", help="JSON is the default output format")
        if name in {"status", "events", "cancel", "pause", "resume", "estimate", "verify"}:
            action.add_argument("job_id")
        if name == "work":
            action.add_argument("--once", action="store_true", help="Run at most one queued job")
        if name == "submit":
            action.add_argument(
                "--dry-run", action="store_true", help="Validate and estimate without queuing"
            )
            action.add_argument("snapshot")
            action.add_argument("--output", required=True, help="New path under project exports/")
            action.add_argument("--start", type=int, default=0)
            action.add_argument("--end", type=int)
            action.add_argument(
                "--chunk-frames",
                type=int,
                help="Maximum video chunk length; default about 30 seconds",
            )
            action.add_argument("--preset", choices=PRESETS)
            action.add_argument("--width", type=int)
            action.add_argument("--height", type=int)
            action.add_argument("--video-bitrate", type=int, help="Requested bits per second")
            action.add_argument("--audio-bitrate", type=int, help="AAC bits per second")
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
        if (args.width is None) != (args.height is None):
            raise ValueError("width and height must be supplied together")
        if args.preset and args.width is not None:
            raise ValueError("choose a preset or custom dimensions, not both")
        profile = preset_profile(
            args.preset or "proxy",
            fps=snapshot.episode.fps,
            encoder=args.encoder,
            video_bitrate=args.video_bitrate,
            audio_gain_db=args.audio_gain_db,
        )
        changes = {}
        if args.width is not None:
            changes.update(id="custom", canvas=Canvas(width=args.width, height=args.height))
        if args.audio_bitrate is not None:
            changes["audio_bitrate"] = args.audio_bitrate
        profile = OutputProfile.model_validate({**profile.model_dump(), **changes})
        result = (service.prepare if args.dry_run else service.submit)(
            args.snapshot,
            profile,
            args.output,
            first_frame=args.start,
            end_frame=args.end,
            max_chunk_frames=args.chunk_frames,
        )
        if args.dry_run:
            result = estimate_storage(assets, result)
    elif name == "list":
        result = service.ledger.all()
    elif name == "status":
        result = service.ledger.get(args.job_id)
    elif name == "estimate":
        result = estimate_storage(assets, service.ledger.get(args.job_id))
    elif name == "verify":
        result = service.verify_export(args.job_id)
    elif name == "events":
        result = service.ledger.events(args.job_id)
    elif name == "cancel":
        result = service.cancel(args.job_id)
    elif name == "pause":
        result = service.pause(args.job_id)
    elif name == "resume":
        result = service.resume(args.job_id)
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
