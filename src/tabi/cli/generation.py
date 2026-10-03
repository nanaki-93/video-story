"""Explicit optional generation commands; no model or extension installer."""

import json
from pathlib import Path
from urllib.parse import quote

from tabi.core.assets import AssetService
from tabi.core.documents import decode_data
from tabi.core.generation import GenerationService
from tabi.core.models.base import AssetRef, content_hash
from tabi.core.models.generation import GenerationPolicy
from tabi.core.persistence import ProjectStore
from tabi.core.preferences import PreferencesService

from .assets import trusted_roots


def add_generation_commands(commands):
    parser = commands.add_parser(
        "generation", help="Allowlisted local ComfyUI workflows and draft imports"
    )
    actions = parser.add_subparsers(dest="generation_command", required=True)
    policy = actions.add_parser("configure", help="Explicitly save the local generation policy")
    policy.add_argument("file", type=Path)
    for name in ("status", "register", "submit", "refresh", "import", "node-info"):
        action = actions.add_parser(name)
        action.add_argument("project", type=Path)
        action.add_argument("--root", action="append", default=[], metavar="ID=PATH")
        if name == "status":
            action.add_argument("--probe", action="store_true")
        elif name == "register":
            action.add_argument("file", type=Path)
        else:
            action.add_argument("identity")
            if name == "submit":
                action.add_argument("version")
                action.add_argument("--expected-hash", required=True)


def run_generation_command(args, settings):
    command = args.generation_command
    if command == "configure":
        policy = GenerationPolicy.model_validate(decode_data(args.file.read_bytes()))
        preferences = PreferencesService(settings)
        before, exists = preferences.read()
        result = preferences.save(
            before.model_copy(update={"generation": policy}), before.revision if exists else None
        )
    else:
        assets = AssetService(
            ProjectStore(args.project),
            roots=trusted_roots(args.root),
            ffmpeg=settings.ffmpeg,
            ffprobe=settings.ffprobe,
        )
        service = GenerationService(assets, settings)
        if command == "status":
            result = service.status(probe=args.probe)
        elif command == "register":
            result = service.register(decode_data(args.file.read_bytes()))
        elif command == "submit":
            result = service.submit(
                AssetRef(id=args.identity, version=args.version), expected_hash=args.expected_hash
            )
        elif command == "refresh":
            result = service.poll(args.identity)
        elif command == "import":
            result = service.import_results(args.identity)
        else:
            values = service._client().request("/object_info/" + quote(args.identity, safe=""))
            if args.identity not in values:
                raise ValueError("that node is not installed on the selected server")
            print(
                json.dumps(
                    {
                        "node": args.identity,
                        "sha256": content_hash(values[args.identity]),
                        "definition": values[args.identity],
                    },
                    indent=2,
                )
            )
            return 0
    print(result.model_dump_json(indent=2))
    return 0
