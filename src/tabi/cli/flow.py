"""Thin CLI over the same assisted Flow services used by the local app."""

import json
from pathlib import Path

from tabi.core.flow.assembly import FlowAssembler
from tabi.core.flow.media import FlowMedia
from tabi.core.flow.review import FlowReview
from tabi.core.flow.runner import FlowRunner
from tabi.core.flow.service import FlowService
from tabi.core.flow.shots import missing_reference, reference_instruction, shot_progress
from tabi.core.models.base import MediaPath
from tabi.core.models.flow import FlowLimits, FlowRecipe, FlowState
from tabi.core.persistence import ProjectStore

from .assets import trusted_roots
from .episodes import project_arguments


def add_flow_commands(commands):
    parser = commands.add_parser("flow", help="Create, continue, review and export a Flow video")
    actions = parser.add_subparsers(dest="flow_command", required=True)
    for name in (
        "create",
        "status",
        "prepare",
        "import",
        "inspect",
        "review",
        "pause",
        "resume",
        "clone",
        "branch",
        "transition",
        "reference",
        "export",
    ):
        command = actions.add_parser(name)
        project_arguments(command)
        if name == "create":
            command.add_argument("--title", default="TABI in Tokyo")
            command.add_argument("--limits", required=True, type=Path)
            command.add_argument("--recipe", type=Path)
        else:
            command.add_argument("identity")
        if name in {
            "prepare",
            "import",
            "inspect",
            "review",
            "pause",
            "resume",
            "branch",
            "transition",
            "reference",
            "export",
        }:
            command.add_argument("--revision", required=True, type=int)
        if name in {"import", "reference"}:
            command.add_argument("--source", required=True, help="Registered ROOT:relative/path")
            command.add_argument("--synthetic", action="store_true")
        if name in {"import", "transition"}:
            command.add_argument("--attempt", required=True)
        if name in {"review", "inspect"}:
            command.add_argument("--candidate", required=True)
        if name == "review":
            command.add_argument("--hash", required=True)
            command.add_argument("--decision", required=True, choices=["accepted", "rejected"])
            command.add_argument("--note", required=True)
            command.add_argument("--state", type=Path)
            command.add_argument("--safe-end", type=int)
            command.add_argument(
                "--correction",
                choices=["particles", "mouth", "identity", "props", "motion", "action"],
            )
        if name == "reference":
            command.add_argument("--key")
            command.add_argument("--state", type=Path)
            command.add_argument("--note")
        if name in {"clone", "reference"}:
            command.add_argument("--title", required=True)
        if name == "branch":
            command.add_argument("--parent")
        if name == "transition":
            command.add_argument(
                "--state", choices=["submitted", "unknown", "failed"], required=True
            )
            command.add_argument("--diagnostic")
            command.add_argument("--credits", type=int)


def run_flow_command(args, settings):
    service = FlowService(ProjectStore(args.project), trusted_roots(args.root))
    runner = FlowRunner(service)
    name = args.flow_command
    if name == "create":
        result = service.create(
            args.title,
            FlowLimits.model_validate_json(args.limits.read_bytes()),
            recipe=FlowRecipe.model_validate_json(args.recipe.read_bytes())
            if args.recipe
            else None,
        )
    elif name == "status":
        episode = service.get(args.identity)
        key = missing_reference(episode)
        print(
            json.dumps(
                {
                    "episode": episode.model_dump(mode="json"),
                    "next_step": runner.status(episode),
                    "shots": shot_progress(episode),
                    "next_reference": {
                        "key": key,
                        "instruction": reference_instruction(episode.recipe, key),
                    }
                    if key
                    else None,
                },
                indent=2,
            )
        )
        return 0
    elif name == "prepare":
        result = runner.prepare(args.identity, args.revision)
    elif name in {"import", "reference"}:
        root, separator, path = args.source.partition(":")
        if not separator:
            raise ValueError("source requires ROOT:relative/path")
        media = FlowMedia(service, settings)
        source = MediaPath(root_id=root, path=path)
        if name == "import":
            result = media.import_result(
                args.identity,
                args.attempt,
                source,
                revision=args.revision,
                synthetic=args.synthetic,
            )
        else:
            reference = media.reference(
                source,
                title=args.title,
                synthetic=args.synthetic,
                key=args.key,
                starting_state=FlowState.model_validate_json(args.state.read_bytes())
                if args.state
                else None,
                review_note=args.note,
            )
            result = service.add_reference(args.identity, reference, args.revision)
    elif name == "inspect":
        result = FlowReview(service, settings).prepare(
            args.identity, args.candidate, revision=args.revision
        )
    elif name == "review":
        result = service.review(
            args.identity,
            args.candidate,
            revision=args.revision,
            media_sha256=args.hash,
            decision=args.decision,
            note=args.note,
            observed_state=FlowState.model_validate_json(args.state.read_bytes())
            if args.state
            else None,
            safe_end_frame=args.safe_end,
            retry_focus=args.correction,
        )
    elif name in {"pause", "resume"}:
        result = runner.pause(args.identity, args.revision, paused=name == "pause")
    elif name == "clone":
        result = service.clone(args.identity, args.title)
    elif name == "branch":
        result = service.branch_from(args.identity, args.parent, args.revision)
    elif name == "transition":
        result = runner.transition(
            args.identity,
            args.attempt,
            revision=args.revision,
            state=args.state,
            diagnostic=args.diagnostic,
            observed_credits=args.credits,
        )
    else:
        assembler = FlowAssembler(service, settings)
        result = assembler.run(assembler.freeze(args.identity, revision=args.revision).id)
    print(result.model_dump_json(indent=2))
    return 0
