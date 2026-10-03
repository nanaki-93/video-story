"""Adapters for implemented core services and bounded media diagnostics."""

import argparse
import json
import os
from pathlib import Path

from tabi import __version__
from tabi.cli.assets import add_asset_commands, run_asset_command
from tabi.cli.audio import add_audio_commands, run_audio_command
from tabi.cli.backup import add_backup_commands, run_backup_command
from tabi.cli.cache import add_cache_commands, run_cache_command
from tabi.cli.episodes import add_episode_commands, run_episode_command
from tabi.cli.jobs import add_job_commands, run_job_command
from tabi.cli.logging import configure_logging
from tabi.cli.publishing import add_release_commands, run_release_command
from tabi.core.config import ConfigError, load_settings
from tabi.core.documents import DocumentError, read_document
from tabi.core.fixtures import generate_fixtures
from tabi.core.models import Episode, Project, ValidationReport
from tabi.core.persistence import ProjectStore, StorageError
from tabi.core.process import ToolError
from tabi.core.render.profiles import PRESETS, preset_profile
from tabi.core.render.spike import ENCODERS, SpikeDependencyError, SpikeError, render_spike
from tabi.core.timeline import Timeline, expand_random_actions, prng_fingerprint
from tabi.core.toolchain import doctor


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
    add_asset_commands(commands)
    add_audio_commands(commands)
    add_backup_commands(commands)
    add_cache_commands(commands)
    add_episode_commands(commands)
    add_job_commands(commands)
    add_release_commands(commands)
    web = commands.add_parser("web", help="Launch the owned, authenticated local web workspace")
    web.add_argument("--root", action="append", default=[], metavar="ID=PATH")
    web.add_argument("--web-root", type=Path, help="Built static UI directory")
    web.add_argument("--no-open", action="store_true", help="Start without opening a browser")
    profiles = commands.add_parser("profiles", help="List explicit SDR export presets")
    profiles.add_argument("--encoder", choices=ENCODERS, default="libx264")
    profiles.add_argument("--fps-num", type=int, default=30)
    profiles.add_argument("--fps-den", type=int, default=1)
    config = commands.add_parser(
        "config", help="Show resolved local settings without changing files"
    )
    config.add_argument("--json", action="store_true", help="Write machine-readable JSON to stdout")
    health = commands.add_parser("doctor", help="Probe local tools and storage; no rendering")
    health.add_argument("--json", action="store_true")
    health.add_argument(
        "--output-dir", type=Path, default=Path.cwd(), help="Existing directory to check"
    )
    spike = commands.add_parser(
        "render-spike", help="Render and verify a synthetic ten-second test"
    )
    spike.add_argument("--output-dir", required=True, type=Path)
    spike.add_argument("--encoder", choices=ENCODERS, default="libx264")
    spike.add_argument("--json", action="store_true")
    fixtures = commands.add_parser("fixtures", help="Generate a new reproducible synthetic project")
    fixtures.add_argument("--output", required=True, type=Path)
    fixtures.add_argument("--profile", choices=["core", "effects", "story"], default="core")
    fixtures.add_argument("--json", action="store_true")
    timeline = commands.add_parser("timeline", help="Evaluate global frames or expand timing")
    timeline_commands = timeline.add_subparsers(dest="timeline_command", required=True)
    inspect_frame = timeline_commands.add_parser("inspect")
    inspect_frame.add_argument("file", type=Path)
    inspect_frame.add_argument("--frame", type=int, required=True)
    expand = timeline_commands.add_parser("expand")
    expand.add_argument("file", type=Path)
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
    if args.command == "timeline":
        try:
            episode = read_document(args.file)
            if not isinstance(episode, Episode):
                raise ValueError("timeline requires an episode document")
            result = (
                Timeline(episode).inspect(args.frame)
                if args.timeline_command == "inspect"
                else {
                    "seed": episode.seed,
                    "prng": prng_fingerprint().model_dump(mode="json"),
                    "actions": [
                        action.model_dump(mode="json") for action in expand_random_actions(episode)
                    ],
                }
            )
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        except (DocumentError, ValueError, OSError) as error:
            logger.error("timeline_failed: %s", error)
            return 2
    if args.command == "fixtures":
        try:
            manifest = generate_fixtures(args.output, profile=args.profile)
        except (DocumentError, StorageError, OSError) as error:
            logger.error("fixture_generation_failed: %s", error)
            return 4
        print(
            manifest.model_dump_json(indent=2)
            if args.json
            else f"Synthetic project: {args.output.resolve()}"
        )
        return 0
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
    if args.command == "web":
        from tabi.api.launcher import launch
        from tabi.cli.assets import trusted_roots

        try:
            roots = trusted_roots(args.root) if args.root else {"projects": settings.project_root}
            return launch(settings, roots, web_root=args.web_root, no_open=args.no_open)
        except (ValueError, OSError) as error:
            logger.error("local_workspace_failed: %s", error)
            return 4
    if args.command == "profiles":
        try:
            print(
                json.dumps(
                    [
                        preset_profile(
                            name,
                            fps={"num": args.fps_num, "den": args.fps_den},
                            encoder=args.encoder,
                        ).model_dump(mode="json")
                        for name in PRESETS
                    ],
                    indent=2,
                )
            )
            return 0
        except ValueError as error:
            logger.error("profile_failed: %s", error)
            return 2
    if args.command == "cache":
        try:
            return run_cache_command(args)
        except (ValueError, DocumentError, StorageError, OSError) as error:
            logger.error("cache_operation_failed: %s", error)
            return 4
    if args.command == "backup":
        try:
            return run_backup_command(args)
        except (ValueError, DocumentError, StorageError, OSError) as error:
            logger.error("backup_operation_failed: %s", error)
            return 4
    if args.command == "release":
        try:
            return run_release_command(args, settings)
        except (ValueError, DocumentError, StorageError, OSError, ToolError) as error:
            logger.error("release_operation_failed: %s", error)
            return 4
    if args.command == "audio":
        try:
            return run_audio_command(args, settings)
        except (ValueError, DocumentError, StorageError, OSError, ToolError) as error:
            logger.error("audio_operation_failed: %s", error)
            return 4
    if args.command in {"compile", "validate", "frame", "preview", "snapshot", "story"}:
        try:
            return run_episode_command(args, settings)
        except DocumentError as error:
            print(error.report().model_dump_json(indent=2))
            return 2
        except (ValueError, OSError, ToolError) as error:
            logger.error("episode_operation_failed: %s", error)
            return 4
    if args.command == "jobs":
        try:
            return run_job_command(args, settings)
        except KeyboardInterrupt:
            logger.error("worker_interrupted: owned work retained for recovery")
            return 130
        except (ValueError, DocumentError, StorageError, OSError, ToolError) as error:
            logger.error("job_operation_failed: %s", error)
            return 4
    if args.command == "asset":
        try:
            return run_asset_command(args, settings)
        except (ValueError, DocumentError, StorageError, OSError, ToolError) as error:
            logger.error("asset_operation_failed: %s", error)
            return 4
    if args.command == "render-spike":
        try:
            report_path = render_spike(settings, args.output_dir, args.encoder)
        except SpikeDependencyError as error:
            logger.error("spike_dependency_missing: %s", error)
            return 3
        except (SpikeError, OSError) as error:
            logger.error("spike_failed: %s", error)
            return 4
        if args.json:
            print(report_path.read_text(encoding="utf-8"), end="")
        else:
            print(f"Verified synthetic test; report: {report_path}")
        return 0
    if args.command == "doctor":
        report = doctor(settings, args.output_dir)
        if args.json:
            print(report.model_dump_json(indent=2))
        else:
            print(
                f"Toolchain {'ready' if report.ready else 'not ready'}; "
                "encoders listed, not render-tested."
            )
            print(f"FFmpeg: {report.ffmpeg.path} ({report.ffmpeg.version})")
            print(f"ffprobe: {report.ffprobe.path} ({report.ffprobe.version})")
            print(f"Output: {report.storage.path}; free bytes: {report.storage.free_bytes}")
            for problem in report.issues:
                print(f"{problem.code}: {problem.message} {problem.suggested_fix}")
        return (
            0
            if report.ready
            else (4 if any(p.code.startswith("storage_") for p in report.issues) else 3)
        )
    if args.json:
        print(json.dumps(settings.as_dict(), ensure_ascii=False, indent=2))
    else:
        for key, value in settings.as_dict().items():
            print(f"{key}: {value}")
    return 0
