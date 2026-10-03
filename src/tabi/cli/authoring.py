"""Portable authoring adapters using the same requests and services as the web UI."""

import json
from pathlib import Path

from tabi.core.assets import AssetService
from tabi.core.authoring import AssetRevision, AuthoringService, NewEpisode, StillTemplate
from tabi.core.documents import read_data
from tabi.core.editor import EditorService, EditRequest
from tabi.core.models import ActionPack
from tabi.core.models.base import AssetRef
from tabi.core.persistence import ProjectStore

from .assets import trusted_roots
from .episodes import project_arguments


def add_author_commands(commands):
    parser = commands.add_parser("author", help="Create, edit and review saved project documents")
    actions = parser.add_subparsers(dest="author_command", required=True)
    for name in (
        "catalog",
        "create-episode",
        "show",
        "edit",
        "lanes",
        "install",
        "still-template",
        "asset-version",
        "metadata",
        "review",
    ):
        action = actions.add_parser(name)
        project_arguments(action)
        if name in {"show", "edit", "lanes"}:
            action.add_argument("episode", help="Saved episode ID")
        if name in {"metadata", "review"}:
            action.add_argument("kind", choices=["scene_template", "action_pack"])
        if name in {"asset-version", "metadata", "review"}:
            action.add_argument("id")
            action.add_argument("version")
        if name in {"create-episode", "edit", "install", "still-template", "asset-version"}:
            action.add_argument("request", type=Path, help="Strict JSON/YAML request or document")
        if name == "install":
            action.add_argument(
                "--expected-revision", type=int, help="Required for an existing draft"
            )
        if name == "review":
            action.add_argument("--reviewed-hash", required=True)
            action.add_argument("--reviewer", required=True)
            action.add_argument("--note", required=True)


def run_author_command(args, settings):
    assets = AssetService(
        ProjectStore(args.project),
        roots=trusted_roots(args.root),
        ffmpeg=settings.ffmpeg,
        ffprobe=settings.ffprobe,
    )
    author = AuthoringService(assets)
    name = args.author_command
    if name == "catalog":
        result = {
            "episodes": [doc.model_dump(mode="json") for doc in author.episodes()],
            "templates": [doc.model_dump(mode="json") for doc in author.templates()],
            "packs": [
                doc.model_dump(mode="json")
                for doc in author.documents("registry/actions", ActionPack)
            ],
        }
    elif name == "show":
        result = author.episode(args.episode)
    elif name == "lanes":
        result = EditorService(assets).lanes(author.episode(args.episode))
    elif name == "create-episode":
        result = author.create_episode(NewEpisode.model_validate(read_data(args.request)))
    elif name == "edit":
        result = EditorService(assets).edit(
            args.episode, EditRequest.model_validate(read_data(args.request))
        )
    elif name == "install":
        result = author.install(read_data(args.request), expected_revision=args.expected_revision)
    elif name == "still-template":
        request = StillTemplate.model_validate(read_data(args.request))
        result = author.still_template(
            request.asset, identity=request.id, version=request.version, camera_id=request.camera_id
        )
    elif name == "asset-version":
        request = AssetRevision.model_validate(read_data(args.request))
        result = author.asset_version(
            AssetRef(id=args.id, version=args.version),
            version=request.version,
            provenance=request.provenance,
            compatibility=request.compatibility,
        )
    elif name == "metadata":
        doc = author.metadata(args.kind, AssetRef(id=args.id, version=args.version))
        result = {
            "document": doc.model_dump(mode="json"),
            "review_content_sha256": doc.approval_hash,
        }
    else:
        result = author.review_metadata(
            args.kind,
            AssetRef(id=args.id, version=args.version),
            expected_hash=args.reviewed_hash,
            reviewer=args.reviewer,
            note=args.note,
        )
    print(
        json.dumps(
            result if isinstance(result, (dict, list)) else result.model_dump(mode="json"),
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0
