"""Atomic local Flow drafts with hash-bound reviews and preserved branches."""

from __future__ import annotations

import hashlib
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
from ..persistence import ProjectStore, RevisionConflict, StorageError, resolve_media_path


class FlowError(StorageError):
    pass


def updated(model, **changes):
    return type(model).model_validate({**model.model_dump(), **changes})


def references_hash(episode: FlowEpisode) -> str:
    return content_hash(
        {"references": [item.model_dump(mode="json") for item in episode.references]}
    )


def default_recipe() -> FlowRecipe:
    routine = [
        ("look-15", "look", 15),
        ("pickup-30", "pickup", 30),
        ("sip", "sip", 37),
        ("return", "return_cup", 42),
        ("sway-45", "sway", 45),
        ("look-60", "look", 60),
        ("breath-75", "deep_breath", 75),
    ]
    return FlowRecipe(
        beats=[
            FlowBeat(id=identity, kind=kind, target_frame=seconds * 24)
            for identity, kind, seconds in routine
        ]
    )


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

    def clone(self, episode_id: str, title: str) -> FlowEpisode:
        episode = self.get(episode_id)
        return self.create(
            title, episode.limits, recipe=episode.recipe, references=episode.references
        )

    def save(self, episode: FlowEpisode, *, expected_revision: int | None) -> FlowEpisode:
        """Publish evidence before the authoritative atomic draft. Orphans are never replayed."""
        if expected_revision is not None:
            previous = self.get(episode.id)
            if previous.revision != expected_revision:
                raise RevisionConflict("Flow draft changed; reload before continuing")
            before = {item.id: item for item in previous.attempts}
            for attempt in episode.attempts:
                old = before.get(attempt.id)
                if old and (
                    old.prompt_sha256 != attempt.prompt_sha256
                    or old.parent_sha256 != attempt.parent_sha256
                    or old.beat != attempt.beat
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
    ) -> FlowEpisode:
        episode = self.get(episode_id)
        candidate = self.candidate(episode, candidate_id)
        if candidate.review != "pending" or candidate.media.sha256 != media_sha256:
            raise FlowError("review is stale or the clip has already been reviewed")
        self.verify_file(candidate.media)
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
        if decision == "accepted":
            parent = active[-1] if active else None
            if candidate.parent_id != parent:
                raise FlowError("clip belongs to an old branch; choose its parent explicitly")
            active = [*active, candidate.id]
        candidate = updated(
            candidate,
            review=decision,
            review_note=note,
            reviewed_sha256=media_sha256,
            observed_state=observed_state,
            trim=trim or candidate.trim,
            safe_end_frame=safe_end_frame,
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

    def get_export(self, identity: str) -> FlowExport:
        from pydantic import TypeAdapter

        from ..models.base import Identifier

        TypeAdapter(Identifier).validate_python(identity)
        document = self.store.read(f"flow/exports/{identity}.json")
        if not isinstance(document, FlowExport):
            raise FlowError("expected a Flow export")
        return document
