"""Episode workflow adapters; no timeline or render semantics live here."""

import json
from pathlib import Path

from tabi.core.assets import AssetService
from tabi.core.documents import read_document
from tabi.core.episodes import EpisodeService
from tabi.core.models import Episode
from tabi.core.models.base import Canvas
from tabi.core.persistence import ProjectStore

from .assets import trusted_roots


def project_arguments(parser):
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--root", action="append", default=[], metavar="ID=PATH")


def add_episode_commands(commands):
    for name in ("validate", "compile"):
        parser = commands.add_parser(
            name, help=f"{name.title()} an episode through the shared compiler"
        )
        parser.add_argument("episode", type=Path)
        parser.add_argument(
            "--purpose", choices=["preview", "synthetic_test", "production"], default="preview"
        )
        project_arguments(parser)
        if name == "compile":
            parser.add_argument(
                "--output", type=Path, help="Optional no-clobber snapshot JSON copy"
            )
    for name in ("frame", "preview"):
        parser = commands.add_parser(name, help="Render from an immutable saved snapshot")
        parser.add_argument("snapshot", help="Saved snapshot SHA-256")
        project_arguments(parser)
        parser.add_argument("--output", type=Path, required=True)
        parser.add_argument("--width", type=int)
        parser.add_argument("--height", type=int)
        if name == "frame":
            parser.add_argument("--frame", type=int, required=True)
        else:
            parser.add_argument("--start", type=int, default=0)
            parser.add_argument("--end", type=int, required=True)
            parser.add_argument("--audio-gain-db", type=float, default=0.0)
            parser.add_argument(
                "--encoder", choices=["libx264", "h264_videotoolbox"], default="libx264"
            )
    parser = commands.add_parser(
        "snapshot", help="Inspect or explicitly review an immutable snapshot"
    )
    actions = parser.add_subparsers(dest="snapshot_command", required=True)
    for name in ("show", "review"):
        command = actions.add_parser(name)
        command.add_argument("snapshot")
        project_arguments(command)
        if name == "review":
            command.add_argument("--reviewed-hash", required=True)
            command.add_argument("--reviewer", required=True)
            command.add_argument("--note", required=True)


def run_episode_command(args, settings):
    assets = AssetService(
        ProjectStore(args.project),
        roots=trusted_roots(args.root),
        ffmpeg=settings.ffmpeg,
        ffprobe=settings.ffprobe,
    )
    service = EpisodeService(assets, settings)
    if args.command in {"compile", "validate"}:
        episode = read_document(args.episode)
        if not isinstance(episode, Episode):
            raise ValueError("an episode document is required")
        result = (
            service.validate(episode, purpose=args.purpose)
            if args.command == "validate"
            else service.compile(episode, purpose=args.purpose, output=args.output)
        )
    elif args.command == "snapshot":
        if args.snapshot_command == "show":
            print(json.dumps(service.inspect_snapshot(args.snapshot), ensure_ascii=False, indent=2))
            return 0
        result = service.review_snapshot(
            args.snapshot, expected_hash=args.reviewed_hash, reviewer=args.reviewer, note=args.note
        )
    else:
        if (args.width is None) != (args.height is None):
            raise ValueError("width and height must be supplied together")
        canvas = Canvas(width=args.width, height=args.height) if args.width is not None else None
        result = (
            service.frame(args.snapshot, args.frame, args.output, canvas=canvas)
            if args.command == "frame"
            else service.preview(
                args.snapshot,
                args.start,
                args.end,
                args.output,
                canvas=canvas,
                encoder=args.encoder,
                audio_gain_db=args.audio_gain_db,
            )
        )
    print(result.model_dump_json(indent=2))
    return 2 if args.command == "validate" and not result.valid else 0
