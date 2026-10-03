"""Audio commands share source, sample and metadata checks with the application."""

from pathlib import Path

from tabi.core.assets import AssetService
from tabi.core.audio import AudioService
from tabi.core.audio.editor import AudioEdit, AudioEditor
from tabi.core.audio.mix import AudioMixer
from tabi.core.documents import read_data, read_document
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
    for name in ("inspect", "waveform", "release-import", "mix"):
        action = actions.add_parser(name)
        project_arguments(action)
        if name == "waveform":
            action.add_argument("id")
            action.add_argument("version")
            action.add_argument("--bins", type=int, default=512)
        elif name == "mix":
            action.add_argument("snapshot")
            action.add_argument("--start-sample", type=int, default=0)
            action.add_argument("--end-sample", type=int)
            action.add_argument("--gain-db", type=float, default=0.0)
        else:
            action.add_argument("file", type=Path)
        action.add_argument(
            "--output",
            type=Path,
            required=name == "mix",
            help="New WAV for mix, otherwise optional new JSON report",
        )
    for name in ("propose", "edit", "audition"):
        action = actions.add_parser(name)
        project_arguments(action)
        action.add_argument("episode", help="Saved episode ID")
        if name == "audition":
            action.add_argument("--expected-revision", type=int, required=True)
            action.add_argument("--start-sample", type=int, default=0)
            action.add_argument("--end-sample", type=int, required=True)
        else:
            action.add_argument("request", type=Path, help="Strict JSON/YAML AudioEdit request")


def run_audio_command(args, settings):
    service = AudioService(
        AssetService(
            ProjectStore(args.project),
            roots=trusted_roots(args.root),
            ffmpeg=settings.ffmpeg,
            ffprobe=settings.ffprobe,
        )
    )
    if args.audio_command in {"propose", "edit", "audition"}:
        editor = AudioEditor(service.assets, settings)
        if args.audio_command == "audition":
            identity, report = editor.audition(
                args.episode, args.expected_revision, args.start_sample, args.end_sample
            )
            import json

            print(
                json.dumps(
                    {
                        "audition_id": identity,
                        "path": str(service.store.root / f"audio/previews/{identity}.wav"),
                        "report": report.model_dump(mode="json"),
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return 0
        request = AudioEdit.model_validate(read_data(args.request))
        if args.audio_command == "edit":
            result = editor.apply(args.episode, request)
        else:
            result, _ = editor.propose(args.episode, request)
        print(result.model_dump_json(indent=2))
        return 2 if args.audio_command == "propose" and not result.can_apply else 0
    if args.audio_command == "mix":
        snapshot = service.store.read_snapshot(args.snapshot)
        result = AudioMixer(service.assets, settings).render(
            snapshot,
            args.output,
            start_sample=args.start_sample,
            end_sample=args.end_sample,
            gain_db=args.gain_db,
        )
    elif args.audio_command == "waveform":
        result = service.waveform(AssetRef(id=args.id, version=args.version), bins=args.bins)
    else:
        document = read_document(args.file)
        if args.audio_command == "inspect" and isinstance(document, Episode):
            result = service.inspect(document)
        elif args.audio_command == "release-import" and isinstance(document, ReleaseRecord):
            result = service.import_release(document)
        else:
            raise ValueError("command needs an episode or release record of the correct type")
    if args.output is not None and args.audio_command != "mix":
        export_document(result, args.output)
    print(result.model_dump_json(indent=2))
    return 0
