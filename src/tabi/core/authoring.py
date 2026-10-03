"""Small shared authoring operations; browser and CLI use portable core documents."""

from datetime import UTC, datetime
from typing import Literal

from pydantic import Field

from .assets import AssetService
from .audio.timeline import prepared_samples
from .documents import validate_data
from .models import ActionPack, Asset, Episode, ReleaseRecord, SceneTemplate, TrackPlacement
from .models.assets import Approval, Compatibility, Provenance
from .models.base import AssetRef, Canvas, Frame, FrameRate, Identifier, Model, Text, version_tuple
from .persistence import RevisionConflict, StorageError, document_path

MetadataKind = Literal["scene_template", "action_pack"]


class NewEpisode(Model):
    id: Identifier
    title: Text
    format: Literal["story", "session", "track"] = "story"
    fps: FrameRate
    canvas: Canvas
    duration_frames: int = Field(gt=0)
    seed: Frame = 0
    template: AssetRef
    body_pose: Identifier = "idle"
    music: list[AssetRef] = Field(default_factory=list)


class AuthoringService:
    def __init__(self, assets: AssetService):
        self.assets, self.store = assets, assets.store

    def documents(self, folder, model):
        result = []
        for path in sorted((self.store.root / folder).glob("**/*.json")):
            doc = self.store.read(path.relative_to(self.store.root).as_posix())
            if (
                not isinstance(doc, model)
                or document_path(doc) != path.relative_to(self.store.root).as_posix()
            ):
                raise ValueError("catalog document identity does not match its path")
            result.append(doc)
        return result

    def templates(self):
        return self.documents("registry/templates", SceneTemplate)

    def metadata(self, kind: MetadataKind, reference: AssetRef):
        reference = AssetRef.model_validate(reference)
        folders = {"scene_template": "templates", "action_pack": "actions"}
        if kind not in folders:
            raise ValueError("review a scene template or action pack")
        path = f"registry/{folders[kind]}/{reference.id}/{reference.version}.json"
        doc = self.store.read(path)
        if doc.document_type != kind or document_path(doc) != path:
            raise ValueError("metadata identity does not match its registry path")
        return doc

    def review_metadata(self, kind, reference, *, expected_hash, reviewer, note):
        """Record explicit content review only after approved dependencies validate."""
        from .timeline.compiler import ActionCompiler

        doc = self.metadata(kind, reference)
        if doc.approval.status == "approved":
            raise StorageError("metadata is already approved; create a new version to edit")
        if doc.approval_hash != expected_hash:
            raise RevisionConflict("reviewed metadata changed; reload and inspect its current hash")
        compiler = ActionCompiler(self.assets, purpose="production")
        # Only this exact reviewed candidate is exempt from prior approval. All
        # dependencies still resolve under production rules, including ID collisions.
        compiler.resolved[(doc.id, doc.version)] = doc
        template = (
            doc
            if isinstance(doc, SceneTemplate)
            else compiler.resolve(doc.template, "scene_template")
        )
        for slot in template.slots:
            for dependency in (slot.asset, slot.mask):
                if dependency:
                    compiler.resolve(dependency, "asset")
        if isinstance(doc, ActionPack):
            compiler.validate_pack(doc, template, doc.fps, doc.outfit_id)
        approval = Approval(
            status="approved",
            content_sha256=expected_hash,
            reviewer=reviewer,
            reviewed_at=datetime.now(UTC),
            note=note,
        )
        reviewed = validate_data(
            {**doc.model_dump(mode="json"), "approval": approval.model_dump(mode="json")}
        )
        return self.store.save_draft(reviewed, expected_revision=doc.revision)

    def episodes(self):
        return self.documents("episodes", Episode)

    def episode(self, identity):
        # Model validation prevents path interpolation of a non-identifier.
        identity = AssetRef(id=identity, version="1.0").id
        doc = self.store.read(f"episodes/{identity}.json")
        if not isinstance(doc, Episode) or doc.id != identity:
            raise ValueError("episode identity differs from its path")
        return doc

    def install(self, data, *, expected_revision=None):
        doc = validate_data(data)
        if not isinstance(doc, (SceneTemplate, ActionPack, Episode, ReleaseRecord)):
            raise ValueError("import an authored template, action pack, episode or release record")
        if isinstance(doc, (SceneTemplate, ActionPack)) and doc.approval.status != "draft":
            raise ValueError("metadata import cannot assert approval; import a draft")
        if isinstance(doc, ReleaseRecord):
            from .audio.service import AudioService

            return AudioService(self.assets).save_release(doc, expected_revision=expected_revision)
        return self.store.save_draft(doc, expected_revision=expected_revision)

    def still_template(self, reference, *, identity, version, camera_id):
        asset = self.assets.require_valid(reference)
        if asset.kind != "still":
            raise ValueError("a still scene needs a still image")
        doc = SceneTemplate(
            schema_version="1.0",
            document_type="scene_template",
            id=identity,
            version=version,
            camera_id=camera_id,
            design_canvas=asset.probe.canvas,
            capabilities=[],
            channels=[],
            anchors={},
            slots=[{"id": "background", "z": 0, "kind": "still", "asset": reference}],
            mask_semantics="white_visible_black_hidden",
        )
        return self.store.save_draft(doc, expected_revision=None)

    def create_episode(self, request: NewEpisode):
        request = NewEpisode.model_validate(request)
        template = self.store.read(
            f"registry/templates/{request.template.id}/{request.template.version}.json"
        )
        if not isinstance(template, SceneTemplate):
            raise ValueError("select a registered scene template")
        cursor, tracks = 0, []
        for index, reference in enumerate(request.music):
            asset = self.assets.require_valid(reference)
            length = prepared_samples(asset)
            tracks.append(
                TrackPlacement(
                    id=f"music-{index + 1}",
                    asset=reference,
                    start_sample=cursor,
                    trim_start_sample=0,
                    trim_end_sample=length,
                )
            )
            cursor += length
        if cursor > request.fps.sample_at(request.duration_frames):
            raise ValueError(
                "music exceeds the episode; increase its frames or edit music explicitly"
            )
        doc = Episode(
            schema_version="1.0",
            document_type="episode",
            id=request.id,
            title=request.title,
            format=request.format,
            fps=request.fps,
            canvas=request.canvas,
            duration_frames=request.duration_frames,
            seed=request.seed,
            tracks=tracks,
            scenes=[
                {
                    "id": "scene-1",
                    "template": request.template,
                    "start_frame": 0,
                    "end_frame": request.duration_frames,
                    "initial_state": {"body_pose": request.body_pose},
                }
            ],
        )
        # Episode files are authoritative. A crash between independent index writes must not
        # hide a saved draft, so the catalog enumerates these files rather than episode_ids.
        return self.store.save_draft(doc, expected_revision=None)

    def asset_version(
        self, reference, *, version, provenance: Provenance, compatibility: Compatibility
    ):
        old = self.assets.require_valid(reference)
        if version_tuple(version) <= version_tuple(old.version):
            raise ValueError("choose a newer asset version")
        data = old.model_dump(mode="json")
        data.update(
            version=version,
            revision=0,
            approval={"status": "draft"},
            provenance=provenance.model_dump(mode="json"),
            compatibility=compatibility.model_dump(mode="json"),
        )
        doc = validate_data(data, model=Asset)
        return self.store.save_draft(doc, expected_revision=None)
