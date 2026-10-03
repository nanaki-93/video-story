"""Only implemented commands are exposed; media commands arrive in later tasks."""

import argparse
import json
import os
from pathlib import Path

from tabi import __version__
from tabi.cli.logging import configure_logging
from tabi.core.config import ConfigError, load_settings
from tabi.core.documents import DocumentError, read_document
from tabi.core.models import Project, ValidationReport
from tabi.core.persistence import ProjectStore, StorageError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="tabi", description="Tabi Story Studio local production tools"
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--config", type=Path, help="Explicit TOML settings file (or TABI_CONFIG)")
    parser.add_argument(
        "--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO", type=str.upper
    )
    commands = parser.add_subparsers(dest="command", required=True)
    config = commands.add_parser(
        "config", help="Show resolved local settings without changing files"
    )
    config.add_argument("--json", action="store_true", help="Write machine-readable JSON to stdout")
    project = commands.add_parser("project", help="Create or inspect a local project")
    project_commands = project.add_subparsers(dest="project_command", required=True)
    init = project_commands.add_parser("init", help="Create a project in a new or empty directory")
    init.add_argument("path", type=Path)
    init.add_argument("--title", required=True)
    init.add_argument("--json", action="store_true")
    show = project_commands.add_parser("show", help="Reopen and inspect a saved project index")
    show.add_argument("path", type=Path)
    show.add_argument("--json", action="store_true")
    document = commands.add_parser(
        "document", help="Validate document structure without media probing"
    )
    document_commands = document.add_subparsers(dest="document_command", required=True)
    validate = document_commands.add_parser(
        "validate", help="Validate JSON/YAML; emit a structural report"
    )
    validate.add_argument("file", type=Path)
    args = parser.parse_args(argv)
    logger = configure_logging(args.log_level)
    if args.command == "document":
        try:
            read_document(args.file)
            report = ValidationReport(
                schema_version="1.0", document_type="validation_report", valid=True, issues=[]
            )
        except DocumentError as error:
            print(error.report().model_dump_json(indent=2))
            return 2
        except OSError as error:
            logger.error("document_io_error: %s", error)
            return 4
        print(report.model_dump_json(indent=2))
        return 0
    if args.command == "project":
        try:
            store = (
                ProjectStore.initialize(args.path, args.title)
                if args.project_command == "init"
                else ProjectStore(args.path)
            )
            saved = store.read()
            if not isinstance(saved, Project):
                raise StorageError("project.json is not a project index")
        except (DocumentError, StorageError) as error:
            logger.error("project_validation_error: %s", error)
            return 2
        except OSError as error:
            logger.error("project_io_error: %s", error)
            return 4
        if args.json:
            print(saved.model_dump_json(indent=2))
        else:
            print(f"{saved.title} (revision {saved.revision}): {store.root}")
        return 0
    try:
        settings = load_settings(args.config, env=os.environ, cwd=Path.cwd(), home=Path.home())
    except ConfigError as error:
        logger.error("configuration_error: %s", error)
        return 2
    logger.info("configuration_resolved")
    if args.json:
        print(json.dumps(settings.as_dict(), ensure_ascii=False, indent=2))
    else:
        for key, value in settings.as_dict().items():
            print(f"{key}: {value}")
    return 0
