"""Thin command adapters for the shared asset registry."""

import json
from pathlib import Path

from tabi.core.assets import AssetService
from tabi.core.config import Settings
from tabi.core.documents import decode_data
from tabi.core.models.base import AssetRef, MediaPath
from tabi.core.models.registry import ImportRequest
from tabi.core.persistence import ProjectStore


def add_asset_commands(commands):
    parser = commands.add_parser("asset", help="Import, inspect, relink and review versioned media")
    actions = parser.add_subparsers(dest="asset_command", required=True)
    for name in ("import", "list", "show", "check", "relink", "approve", "proxy"):
        action = actions.add_parser(name)
        action.add_argument("project", type=Path)
        action.add_argument(
            "--root",
            action="append",
            default=[],
            metavar="ID=PATH",
            help="Explicit trusted external root; repeat as needed",
        )
        if name == "import":
            action.add_argument("request", type=Path, help="Strict JSON/YAML import request")
        elif name != "list":
            action.add_argument("id")
            action.add_argument("version")
        if name == "relink":
            action.add_argument(
                "--paths", required=True, type=Path, help="JSON ordered MediaPath list"
            )
        if name in {"relink", "proxy"}:
            action.add_argument("--new-version", required=True)
        if name == "proxy":
            action.add_argument("--max-edge", type=int, default=640)
        if name == "approve":
            action.add_argument("--reviewed-hash", required=True)
            action.add_argument("--reviewer", required=True)
            action.add_argument("--note", required=True)


def trusted_roots(entries: list[str]) -> dict[str, Path]:
    roots = {}
    for entry in entries:
        key, separator, value = entry.partition("=")
        if not separator or not value or key in roots:
            raise ValueError("root must be a unique ID=PATH")
        MediaPath(root_id=key, path="root-validation")
        roots[key] = Path(value).expanduser().resolve()
    return roots


def run_asset_command(args, settings: Settings) -> int:
    service = AssetService(
        ProjectStore(args.project),
        roots=trusted_roots(args.root),
        ffmpeg=settings.ffmpeg,
        ffprobe=settings.ffprobe,
    )
    command = args.asset_command
    if command == "import":
        result = service.import_asset(
            ImportRequest.model_validate(decode_data(args.request.read_bytes()))
        )
    elif command == "list":
        print(
            json.dumps(
                [asset.model_dump(mode="json") for asset in service.list_assets()],
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    else:
        ref = AssetRef(id=args.id, version=args.version)
        if command == "show":
            result = service.load(ref)
        elif command == "check":
            result = service.check(ref)
        elif command == "relink":
            raw = json.loads(args.paths.read_bytes())
            if not isinstance(raw, list):
                raise ValueError("relink paths must be an ordered JSON list")
            result = service.relink(
                ref, version=args.new_version, paths=[MediaPath.model_validate(p) for p in raw]
            )
        elif command == "proxy":
            result = service.image_proxies(ref, version=args.new_version, max_edge=args.max_edge)
        else:
            result = service.approve(
                ref, expected_hash=args.reviewed_hash, reviewer=args.reviewer, note=args.note
            )
    print(result.model_dump_json(indent=2))
    return 2 if command == "check" and not result.media_valid else 0
