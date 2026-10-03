"""Explicit audio edits and auditions; never trim masters or retime visual story intent."""

from uuid import uuid4

from pydantic import Field, TypeAdapter, ValidationError

from ..authoring import AuthoringService
from ..episodes import EpisodeService
from ..models import Episode, TrackPlacement
from ..models.audio import AudioEditPlan, AudioMixReport
from ..models.base import Frame, Identifier, Model, canonical_bytes
from ..persistence import RevisionConflict
from ..timeline.compiler import ActionCompiler
from .mix import AudioMixer
from .service import AudioService


class AudioEdit(Model):
    expected_revision: Frame
    tracks: list[TrackPlacement] = Field(max_length=1000)
    resequence_music: bool = False


class AudioEditor:
    def __init__(self, assets, settings):
        self.assets, self.store, self.settings = assets, assets.store, settings
        self.author = AuthoringService(assets)

    def propose(self, identity, edit):
        edit = AudioEdit.model_validate(edit)
        episode = self.author.episode(identity)
        if edit.expected_revision != episode.revision:
            raise RevisionConflict("Audio draft changed; reload before applying this edit")
        tracks, cursor = [], 0
        for track in edit.tracks:
            if edit.resequence_music and track.role == "music":
                track = TrackPlacement.model_validate(
                    {**track.model_dump(), "start_sample": cursor}
                )
                cursor += track.duration_samples
            tracks.append(track)
        effective = max((t.start_sample + t.duration_samples for t in tracks), default=0)
        duration = episode.fps.sample_at(episode.duration_frames)
        issues, candidate = [], None
        if effective > duration:
            issues.append(
                f"Audio ends at sample {effective}, beyond story end {duration}. "
                "Edit the trims/placements or extend the story explicitly."
            )
        try:
            candidate = Episode.model_validate({**episode.model_dump(), "tracks": tracks})
            ActionCompiler(self.assets, purpose="preview").compile(candidate)
            AudioService(self.assets).inspect(candidate)
        except (ValueError, OSError) as error:
            if isinstance(error, ValidationError):
                issues.extend(item["msg"] for item in error.errors(include_input=False))
            else:
                issues.append(str(error))
        return AudioEditPlan(
            schema_version="1.0",
            episode_id=identity,
            revision=episode.revision,
            tracks=tracks,
            effective_end_sample=effective,
            episode_duration_samples=duration,
            can_apply=not issues,
            issues=issues,
        ), candidate

    def apply(self, identity, edit):
        edit = AudioEdit.model_validate(edit)
        plan, candidate = self.propose(identity, edit)
        if not plan.can_apply:
            raise ValueError("\n".join(plan.issues))
        return self.store.save_draft(candidate, expected_revision=edit.expected_revision)

    def audition(self, identity, expected_revision, first, end):
        episode = self.author.episode(identity)
        if episode.revision != expected_revision:
            raise RevisionConflict("Audio changed; reload before auditioning")
        if not 0 <= first < end <= episode.fps.sample_at(episode.duration_frames):
            raise ValueError("Audition sample range must be inside the saved episode")
        if end - first > 120 * 48000:
            raise ValueError(
                "Audio auditions are bounded to 120 seconds; choose a smaller sample range"
            )
        with self.store.exclusive_lock(".audio-audition.lock"):
            compiled = EpisodeService(self.assets, self.settings).compile(episode)
            identity = uuid4().hex
            with self.store._directory(("audio", "previews"), create=True):
                pass
            report = AudioMixer(self.assets, self.settings).render(
                self.store.read_snapshot(compiled.snapshot_sha256),
                self.store.root / f"audio/previews/{identity}.wav",
                start_sample=first,
                end_sample=end,
            )
            self.store._atomic_write(
                f"audio/previews/{identity}.json", canonical_bytes(report), overwrite=False
            )
            return identity, report

    def audition_report(self, identity):
        TypeAdapter(Identifier).validate_python(identity)
        report = self.store.read(f"audio/previews/{identity}.json")
        if not isinstance(report, AudioMixReport):
            raise ValueError("Not an audio audition report")
        return f"audio/previews/{identity}.wav", report
