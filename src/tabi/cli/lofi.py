"""CLI adapter for the same reusable-scene service used by the local app."""

import json
from pathlib import Path

from tabi.core.assets import AssetService
from tabi.core.documents import read_data
from tabi.core.lofi import LofiService
from tabi.core.models.lofi import CreateLofiVideo, SaveLofiScene
from tabi.core.persistence import ProjectStore

from .assets import trusted_roots


def add_lofi_command(commands):
    parser = commands.add_parser("lofi", help="Reusable artwork, scenery and loop scenes")
    actions = parser.add_subparsers(dest="lofi_command", required=True)
    for name in ("list", "save", "create-video"):
        action = actions.add_parser(name)
        action.add_argument("--project", type=Path, required=True)
        action.add_argument("--root", action="append", default=[])
        if name != "list":
            action.add_argument("request", type=Path)


def run_lofi_command(args, settings):
    service = LofiService(
        AssetService(
            ProjectStore(args.project),
            roots=trusted_roots(args.root),
            ffmpeg=settings.ffmpeg,
            ffprobe=settings.ffprobe,
        )
    )
    if args.lofi_command == "list":
        result = [scene.model_dump(mode="json") for scene in service.scenes()]
    elif args.lofi_command == "save":
        request = SaveLofiScene.model_validate(read_data(args.request))
        result = service.save(
            request.scene,
            expected_revision=request.expected_revision,
            timing_seconds=request.timing_seconds,
        ).model_dump(mode="json")
    else:
        result = service.create_video(
            CreateLofiVideo.model_validate(read_data(args.request))
        ).model_dump(mode="json")
    print(json.dumps(result, ensure_ascii=False))
    return 0
