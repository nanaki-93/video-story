"""Only implemented commands are exposed; media commands arrive in later tasks."""

import argparse
import json
import os
from pathlib import Path

from tabi import __version__
from tabi.cli.logging import configure_logging
from tabi.core.config import ConfigError, load_settings


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
    args = parser.parse_args(argv)
    logger = configure_logging(args.log_level)
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
