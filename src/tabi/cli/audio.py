"""Audio commands share source, sample and metadata checks with the application."""

from pathlib import Path

from tabi.core.assets import AssetService
from tabi.core.audio import AudioService
from tabi.core.documents import read_document
from tabi.core.export import export_document
from tabi.core.models import Episode, ReleaseRecord
from tabi.core.models.base import AssetRef
from tabi.core.persistence import ProjectStore

from .assets import trusted_roots
from .episodes import project_arguments


def add_audio_commands(commands):
    parser = commands.add_parser(
        "audio", help="Inspect sample timing, waveforms and music metadata"
    )
    actions = parser.add_subparsers(dest="audio_command", required=True)
    for name in ("inspect", "waveform", "release-import"):
        action = actions.add_parser(name)
        project_arguments(action)
        if name == "waveform":
            action.add_argument("id")
            action.add_argument("version")
            action.add_argument("--bins", type=int, default=512)
        else:
            action.add_argument("file", type=Path)
        action.add_argument("--output", type=Path, help="Optional new JSON report copy")


def run_audio_command(args, settings):
    service = AudioService(
        AssetService(
            ProjectStore(args.project),
            roots=trusted_roots(args.root),
            ffmpeg=settings.ffmpeg,
            ffprobe=settings.ffprobe,
        )
    )
    if args.audio_command == "waveform":
        result = service.waveform(AssetRef(id=args.id, version=args.version), bins=args.bins)
    else:
        document = read_document(args.file)
        if args.audio_command == "inspect" and isinstance(document, Episode):
            result = service.inspect(document)
        elif args.audio_command == "release-import" and isinstance(document, ReleaseRecord):
            result = service.import_release(document)
        else:
            raise ValueError("command needs an episode or release record of the correct type")
    if args.output is not None:
        export_document(result, args.output)
    print(result.model_dump_json(indent=2))
    return 0
