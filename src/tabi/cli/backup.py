"""Private backups use the same checked Python services as the local UI."""

from pathlib import Path

from tabi.core.assets import AssetService
from tabi.core.persistence import ProjectStore
from tabi.core.portability import BackupService

from .assets import trusted_roots


def add_backup_commands(commands):
    parser = commands.add_parser("backup", help="Export, verify or restore a private project copy")
    actions = parser.add_subparsers(dest="backup_command", required=True)
    for name in ("export", "inspect", "restore"):
        action = actions.add_parser(name)
        action.add_argument("source", type=Path)
        if name != "inspect":
            action.add_argument(
                "destination", type=Path, help="New sibling folder; never overwritten"
            )
        if name == "export":
            action.add_argument("--root", action="append", default=[], metavar="ID=PATH")


def run_backup_command(args):
    if args.backup_command == "export":
        service = BackupService(
            AssetService(ProjectStore(args.source), roots=trusted_roots(args.root))
        )
        result = service.export(args.destination)
    elif args.backup_command == "restore":
        result = BackupService.restore(args.source, args.destination)
    else:
        result = BackupService.inspect(args.source)
    print(result.model_dump_json(indent=2))
    return 0
