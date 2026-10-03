"""Inspect managed cache entries; pruning requires an explicit observed inventory."""

from pathlib import Path

from tabi.core.cache.store import CacheStore
from tabi.core.persistence import ProjectStore


def add_cache_commands(commands):
    parser = commands.add_parser("cache", help="Inspect or explicitly prune project caches")
    actions = parser.add_subparsers(dest="cache_command", required=True)
    for name in ("inspect", "prune"):
        action = actions.add_parser(name)
        action.add_argument("--project", required=True, type=Path)
        if name == "prune":
            selection = action.add_mutually_exclusive_group(required=True)
            selection.add_argument("--key", action="append", help="Select an observed cache key")
            selection.add_argument("--all", action="store_true", help="All unprotected entries")
            action.add_argument("--apply", action="store_true", help="Delete selected cache files")
            action.add_argument("--inventory", help="Observed inventory SHA-256; required to apply")


def run_cache_command(args):
    cache = CacheStore(ProjectStore(args.project))
    inventory = cache.inventory()
    if args.cache_command == "inspect" or not args.apply:
        print(inventory.model_dump_json(indent=2))
        return 0
    if not args.inventory:
        raise ValueError("inspect first, then pass --inventory SHA with --apply")
    keys = (
        [entry.key for entry in inventory.entries if not entry.protected] if args.all else args.key
    )
    print(cache.prune(keys, expected_inventory=args.inventory).model_dump_json(indent=2))
    return 0
