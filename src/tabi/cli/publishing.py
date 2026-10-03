"""Local release preparation. No network or publishing actions."""

from pathlib import Path

from tabi.core.assets import AssetService
from tabi.core.documents import read_document
from tabi.core.models.publishing import ReleasePreparation
from tabi.core.persistence import ProjectStore
from tabi.core.publishing import ReleaseService

from .assets import trusted_roots
from .episodes import project_arguments


def add_release_commands(commands):
    parser = commands.add_parser("release", help="Prepare factual local bundles for manual release")
    actions = parser.add_subparsers(dest="release_command", required=True)
    for name in ("save", "inspect", "review", "export"):
        action = actions.add_parser(name)
        project_arguments(action)
        if name == "save":
            action.add_argument("file", type=Path)
            action.add_argument("--expected-revision", type=int)
        else:
            action.add_argument("id")
        if name == "review":
            action.add_argument("--kind", required=True, choices=["creative", "metadata"])
            action.add_argument("--expected-hash", required=True)
            action.add_argument("--expected-revision", required=True, type=int)
            action.add_argument("--reviewer", required=True)
            action.add_argument("--note", required=True)
        if name == "export":
            action.add_argument("--bundle-id", required=True)
            action.add_argument("--require-ready", action="store_true")


def run_release_command(args, settings):
    assets = AssetService(
        ProjectStore(args.project),
        roots=trusted_roots(args.root),
        ffmpeg=settings.ffmpeg,
        ffprobe=settings.ffprobe,
    )
    service = ReleaseService(assets, settings)
    if args.release_command == "save":
        preparation = read_document(args.file)
        if not isinstance(preparation, ReleasePreparation):
            raise ValueError("release save requires a release_preparation document")
        result = service.save(preparation, expected_revision=args.expected_revision)
    elif args.release_command == "inspect":
        result = service.inspect(service.load(args.id))
    elif args.release_command == "review":
        result = service.review(
            args.id,
            kind=args.kind,
            expected_hash=args.expected_hash,
            expected_revision=args.expected_revision,
            reviewer=args.reviewer,
            note=args.note,
        )
    else:
        result = service.export(args.id, args.bundle_id, require_ready=args.require_ready)
    print(result.model_dump_json(indent=2))
    return 0
