"""Atomic local Flow drafts with hash-bound reviews and preserved branches."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from uuid import uuid4

from ..models.base import FrameInterval, HashedFile, canonical_bytes, content_hash
from ..models.flow import (
    FlowBeat,
    FlowCandidate,
    FlowEpisode,
    FlowExport,
    FlowLimits,
    FlowRecipe,
    FlowReference,
    FlowState,
)
from ..persistence import (
    ProjectBusy,
    ProjectStore,
    RevisionConflict,
    StorageError,
    resolve_media_path,
)
from .shots import (
    continuity_issue,
    frames_in_shot,
    planned_recipe,
    reference_for,
    required_references,
    shot_by_id,
)


class FlowError(StorageError):
    pass


def updated(model, **changes):
    return type(model).model_validate({**model.model_dump(), **changes})


def references_hash(episode: FlowEpisode) -> str:
    return content_hash(
        {"references": [item.model_dump(mode="json") for item in episode.references]}
    )


def default_recipe() -> FlowRecipe:
    return planned_recipe()


class FlowService:
    def __init__(self, store: ProjectStore, media_roots: dict[str, Path] | None = None):
        self.store = store
        self.media_roots = media_roots or {}

    def get(self, episode_id: str) -> FlowEpisode:
        # Contract validation keeps IDs out of path syntax.
        from pydantic import TypeAdapter

        from ..models.base import Identifier

        TypeAdapter(Identifier).validate_python(episode_id)
        episode = self.store.read(f"flow/episodes/{episode_id}.json")
        if not isinstance(episode, FlowEpisode):
            raise FlowError("expected a Flow episode")
        return episode

    def list(self) -> list[FlowEpisode]:
        folder = self.store.root / "flow/episodes"
        return [self.get(path.stem) for path in sorted(folder.glob("*.json"))]

    def create(
        self,
        title: str,
        limits: FlowLimits,
        *,
        recipe: FlowRecipe | None = None,
        references: list[FlowReference] | None = None,
        identity: str | None = None,
    ) -> FlowEpisode:
        episode = FlowEpisode(
            schema_version="1.0",
            id=identity or uuid4().hex,
            title=title,
            recipe=recipe or default_recipe(),
            references=references or [],
            limits=limits,
        )
        for reference in episode.references:
            self.verify_file(reference.media)
        return self.save(episode, expected_revision=None)

    def clone(self, episode_id: str, title: str, *, recipe=None, limits=None) -> FlowEpisode:
        episode = self.get(episode_id)
        recipe = recipe or episode.recipe
        same_base = all(
            getattr(recipe, key) == getattr(episode.recipe, key)
            for key in ("identity", "outfit", "setting", "camera", "exterior", "opening_inventory")
        )
        references = []
        if same_base:
            if not recipe.shots and not episode.recipe.shots:
                references = episode.references
            elif recipe.shots and episode.recipe.shots:
                old_views = {s.reference_key: (s.framing, s.exterior) for s in episode.recipe.shots}
                matching = {
                    s.reference_key
                    for s in recipe.shots
                    if old_views.get(s.reference_key) == (s.framing, s.exterior)
                }
                references = [r for r in episode.references if r.key in matching]
        return self.create(
            title,
            limits or episode.limits,
            recipe=recipe,
            references=references,
        )

    def add_reference(self, episode_id, reference, revision):
        episode = self.get(episode_id)
        if episode.attempts:
            raise FlowError("Start a variation to change references after generation began.")
        if episode.recipe.shots and reference.key not in required_references(episode.recipe):
            raise FlowError("Choose a reference view from the shot plan.")
        self.verify_file(reference.media)
        refs = [r for r in episode.references if reference.key is None or r.key != reference.key]
        return self.save(
            updated(episode, references=[*refs, reference]), expected_revision=revision
        )

    def save(self, episode: FlowEpisode, *, expected_revision: int | None) -> FlowEpisode:
        """Publish evidence before the authoritative atomic draft. Orphans are never replayed."""
        if expected_revision is not None:
            previous = self.get(episode.id)
            if previous.revision != expected_revision:
                raise RevisionConflict("Flow draft changed; reload before continuing")
            if previous.attempts and (
                previous.references != episode.references or previous.recipe != episode.recipe
            ):
                raise FlowError("Started recipes and references are immutable; create a variation.")
            before = {item.id: item for item in previous.attempts}
            for attempt in episode.attempts:
                old = before.get(attempt.id)
                if old and (
                    old.prompt_sha256 != attempt.prompt_sha256
                    or old.parent_sha256 != attempt.parent_sha256
                    or old.beat != attempt.beat
                    or old.shot_id != attempt.shot_id
                    or old.mode != attempt.mode
                    or old.recipe_sha256 != attempt.recipe_sha256
                    or old.references_sha256 != attempt.references_sha256
                ):
                    raise FlowError("an attempt's prompt, beat and parent are immutable")
            if not set(before).issubset({item.id for item in episode.attempts}):
                raise FlowError("attempt history cannot be erased")
        revision = 0 if expected_revision is None else expected_revision + 1
        evidence = updated(episode, revision=revision)
        self._immutable(f"flow/history/{episode.id}/{content_hash(evidence)}.json", evidence)
        for attempt in episode.attempts:
            self._immutable(f"flow/attempts/{attempt.id}/{content_hash(attempt)}.json", attempt)
        return self.store.save_draft(episode, expected_revision=expected_revision)

    def _immutable(self, relative: str, model):
        payload = canonical_bytes(model)
        with self.store.writer_lock():
            try:
                previous = self.store._read_bytes(relative)
            except FileNotFoundError:
                self.store._atomic_write(relative, payload, overwrite=False)
            else:
                if previous != payload:
                    raise FlowError("immutable evidence has changed")

    def verify_file(self, media: HashedFile) -> Path:
        path = resolve_media_path(media.location, self.store.root, self.media_roots)
        try:
            with path.open("rb") as source:
                digest = hashlib.file_digest(source, "sha256").hexdigest()
        except OSError as error:
            raise FlowError("source is missing or inaccessible; reimport it") from error
        if digest != media.sha256 or path.stat().st_size != media.size_bytes:
            raise FlowError("source content changed; its previous review is no longer valid")
        return path

    def candidate(self, episode: FlowEpisode, candidate_id: str) -> FlowCandidate:
        candidate = next((item for item in episode.candidates if item.id == candidate_id), None)
        if candidate is None:
            raise FlowError("clip does not belong to this video")
        return candidate

    def branch_from(self, episode_id: str, parent_id: str | None, revision: int) -> FlowEpisode:
        episode = self.get(episode_id)
        if parent_id is None:
            active = []
        elif parent_id in episode.accepted_ids:
            active = episode.accepted_ids[: episode.accepted_ids.index(parent_id) + 1]
        else:
            raise FlowError("choose a reviewed clip in the active branch")
        return self.save(updated(episode, accepted_ids=active), expected_revision=revision)

    def review(
        self,
        episode_id: str,
        candidate_id: str,
        *,
        revision: int,
        media_sha256: str,
        decision: str,
        note: str,
        observed_state: FlowState | None = None,
        trim: FrameInterval | None = None,
        safe_end_frame: int | None = None,
        retry_focus: str | None = None,
    ) -> FlowEpisode:
        episode = self.get(episode_id)
        candidate = self.candidate(episode, candidate_id)
        if candidate.review != "pending" or candidate.media.sha256 != media_sha256:
            raise FlowError("review is stale or the clip has already been reviewed")
        self.verify_file(candidate.media)
        if candidate.review_packet:
            packet = json.loads(self.store._read_bytes(candidate.review_packet))
            if (
                packet.get("candidate_sha256") != candidate.media.sha256
                or packet.get("parent_sha256") != candidate.parent_sha256
                or packet.get("reference_hashes")
                != [item.media.sha256 for item in episode.references]
                or (
                    "candidate_trim" in packet
                    and packet["candidate_trim"] != candidate.trim.model_dump(mode="json")
                )
            ):
                raise FlowError("review packet no longer matches the clip, parent or references")
            for image in packet["images"]:
                self.verify_file(HashedFile.model_validate(image["media"]))
            if packet.get("join_video"):
                self.verify_file(HashedFile.model_validate(packet["join_video"]))
            if packet.get("selected_video"):
                self.verify_file(HashedFile.model_validate(packet["selected_video"]))
        attempt = next(item for item in episode.attempts if item.id == candidate.attempt_id)
        if attempt.recipe_sha256 != content_hash(episode.recipe) or (
            attempt.references_sha256 != references_hash(episode)
        ):
            raise FlowError("settings or references changed; prepare a new attempt")
        for reference in episode.references:
            self.verify_file(reference.media)
        if decision not in {"accepted", "rejected"}:
            raise FlowError("choose Accept or Retry")
        active = episode.accepted_ids
        chosen_trim = trim or candidate.trim
        if decision == "accepted":
            from .runner import action_complete, completed_beats

            if not action_complete(attempt.beat, observed_state):
                raise FlowError("the requested action is incomplete; retry from the clean parent")
            parent = active[-1] if active else None
            if candidate.parent_id != parent:
                raise FlowError("clip belongs to an old branch; choose its parent explicitly")
            if episode.recipe.shots:
                shot = shot_by_id(episode, attempt.shot_id)
                remaining = shot.duration_frames - frames_in_shot(episode, shot)
                cut = candidate.trim.start_frame + remaining
                if chosen_trim.start_frame != candidate.trim.start_frame:
                    raise FlowError("Keep the imported starting frame for this shot.")
                if chosen_trim != candidate.trim and chosen_trim.end_frame != cut:
                    raise FlowError("Trim only at the planned shot boundary.")
                if chosen_trim.end_frame > cut:
                    if safe_end_frame != cut:
                        raise FlowError(
                            f"Review the shot ending at clip frame {cut} before accepting."
                        )
                    chosen_trim = FrameInterval(start_frame=chosen_trim.start_frame, end_frame=cut)
                if chosen_trim.end_frame < candidate.trim.end_frame and safe_end_frame != cut:
                    raise FlowError("A shortened shot needs its exact reviewed ending.")
                if chosen_trim.end_frame == cut:
                    done = completed_beats(episode) | {attempt.beat.id}
                    if any(b.id not in done for b in shot.beats):
                        raise FlowError(
                            "Complete this shot's remaining actions before its final cut."
                        )
                    index = episode.recipe.shots.index(shot)
                    if index + 1 < len(episode.recipe.shots):
                        next_ref = reference_for(episode, episode.recipe.shots[index + 1])
                        if next_ref is None:
                            raise FlowError(
                                "Prepare the next shot's clean reference before accepting."
                            )
                        issue = continuity_issue(observed_state, next_ref.starting_state)
                        if issue:
                            raise FlowError(issue)
            active = [*active, candidate.id]
        candidate = updated(
            candidate,
            review=decision,
            review_note=note,
            reviewed_sha256=media_sha256,
            observed_state=observed_state,
            trim=chosen_trim,
            safe_end_frame=safe_end_frame,
            retry_focus=retry_focus,
        )
        return self.save(
            updated(
                episode,
                candidates=[
                    candidate if item.id == candidate.id else item for item in episode.candidates
                ],
                accepted_ids=active,
            ),
            expected_revision=revision,
        )

    def save_export(self, export: FlowExport, *, expected_revision: int | None) -> FlowExport:
        if expected_revision is not None:
            previous = self.get_export(export.id)
            if previous.inputs_sha256 != export.inputs_sha256:
                raise FlowError("export inputs are immutable; create a new export")
        self._immutable(f"flow/inputs/{export.inputs_sha256}.json", export.inputs)
        return self.store.save_draft(export, expected_revision=expected_revision)

    def preview_prompt(self, episode_id: str, beat: FlowBeat, *, parent_id: str | None = None):
        from .prompts import compile_prompt

        episode = self.get(episode_id)
        parent = self.candidate(episode, parent_id) if parent_id else None
        if parent:
            self.verify_file(parent.media)
        for reference in episode.references:
            self.verify_file(reference.media)
        return compile_prompt(episode, beat, parent)

    def get_export(self, identity: str) -> FlowExport:
        from pydantic import TypeAdapter

        from ..models.base import Identifier

        TypeAdapter(Identifier).validate_python(identity)
        document = self.store.read(f"flow/exports/{identity}.json")
        if not isinstance(document, FlowExport):
            raise FlowError("expected a Flow export")
        return document

    def exports(self, episode_id=None):
        folder = self.store.root / "flow/exports"
        return [
            item
            for path in sorted(folder.glob("*.json"))
            if (item := self.get_export(path.stem))
            and (episode_id is None or item.episode_id == episode_id)
        ]

    def recover_exports(self):
        for export in self.exports():
            if export.state != "running":
                continue
            try:
                with self.store.exclusive_lock(f"flow/locks/{export.id}.lock"):
                    current = self.get_export(export.id)
                    if current.state == "running":
                        self.save_export(
                            updated(
                                current,
                                state="interrupted",
                                owner=None,
                                diagnostic="Local worker stopped. Resume this frozen export.",
                            ),
                            expected_revision=current.revision,
                        )
            except ProjectBusy:
                pass  # A live lease owns it; never adopt a persisted PID.
