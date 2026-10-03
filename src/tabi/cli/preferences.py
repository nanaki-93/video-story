"""Revision/hash-guarded local preferences through the shared settings service."""

import json
from pathlib import Path

from tabi.core.documents import read_data
from tabi.core.preferences import PreferencesService, SavePreferences, SaveTools


def add_preferences_commands(commands):
    parser = commands.add_parser("preferences", help="Read or save guarded local settings")
    actions = parser.add_subparsers(dest="preferences_command", required=True)
    for name in ("show", "save", "tools"):
        action = actions.add_parser(name)
        if name != "show":
            action.add_argument(
                "request", type=Path, help="Strict JSON/YAML guarded settings request"
            )


def run_preferences_command(args, settings):
    service = PreferencesService(settings)
    if args.preferences_command == "show":
        preferences, exists = service.read()
        result = {
            "preferences": preferences.model_dump(mode="json"),
            "preferences_saved": exists,
            "config_sha256": service.config_hash(),
            **settings.as_dict(),
        }
    elif args.preferences_command == "save":
        request = SavePreferences.model_validate(read_data(args.request))
        result = service.save(request.preferences, request.expected_revision).model_dump(
            mode="json"
        )
    else:
        request = SaveTools.model_validate(read_data(args.request))
        result = {
            "config_sha256": service.save_tools(**request.model_dump()),
            "restart_required": True,
        }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0
