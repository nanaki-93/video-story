"""Small asset-to-episode adapter using the existing compiler, mixer and render jobs."""

from fractions import Fraction
from math import ceil

from PIL import Image

from .assets import AssetService
from .audio.timeline import prepared_samples
from .authoring import AuthoringService, NewEpisode
from .models import Episode, SceneTemplate
from .models.base import AssetRef, content_hash
from .models.lofi import CreateLofiVideo, LofiScene, OverlaySeconds
from .persistence import RevisionConflict, document_path
from .timeline.compiler import ActionCompiler
from .timeline.effects import visible_canvas


class LofiService:
    def __init__(self, assets: AssetService):
        self.assets, self.store = assets, assets.store

    def scenes(self):
        return AuthoringService(self.assets).documents("registry/lofi", LofiScene)

    def scene(self, reference):
        reference = AssetRef.model_validate(reference)
        scene = self.store.read(f"registry/lofi/{reference.id}/{reference.version}.json")
        if not isinstance(scene, LofiScene) or (scene.id, scene.version) != (
            reference.id,
            reference.version,
        ):
            raise ValueError("scene identity differs from its registered path")
        return scene

    def validate(self, scene):
        scene = LofiScene.model_validate(scene)
        master = self.assets.require_valid(scene.master)
        if master.kind != "still":
            raise ValueError("choose a still master illustration")
        canvas = visible_canvas(master)

        def mask(reference):
            source = self.assets.require_valid(reference)
            if source.kind != "mask" or visible_canvas(source) != canvas:
                raise ValueError("mask must be grayscale and match the master illustration")
            return source

        if scene.window_mask:
            window = mask(scene.window_mask)
            with Image.open(self.assets.resolve(window.files[0].location)) as image:
                crop = window.compatibility.crop
                if crop:
                    image = image.crop((crop.x, crop.y, crop.x + crop.width, crop.y + crop.height))
                if image.getextrema() == (0, 0):
                    raise ValueError("window mask hides everything; white marks the visible view")
        for layer in scene.scenery:
            source = self.assets.require_valid(layer.asset)
            size = visible_canvas(source)
            if (
                source.kind != "still"
                or size.height != canvas.height
                or size.width < layer.repeat_width + canvas.width
            ):
                raise ValueError(
                    "scenery needs the master height and repeat width + master width of padding"
                )
            with Image.open(self.assets.resolve(source.files[0].location)) as raw:
                image = raw.convert("RGBA")
                crop = source.compatibility.crop
                if crop:
                    image = image.crop((crop.x, crop.y, crop.x + crop.width, crop.y + crop.height))
                left = image.crop((0, 0, canvas.width, canvas.height))
                right = image.crop(
                    (layer.repeat_width, 0, layer.repeat_width + canvas.width, canvas.height)
                )
                if left.tobytes() != right.tobytes():
                    raise ValueError("scenery padding must repeat its opening pixels exactly")
        for layer in scene.overlays:
            source = self.assets.require_valid(layer.asset)
            if (
                source.kind != "sequence"
                or visible_canvas(source) != canvas
                or source.probe.fps != scene.fps
                or source.probe.alpha_mode not in {"straight", "premultiplied"}
                or layer.timing.source.end_frame > source.probe.frame_count
            ):
                raise ValueError(
                    "overlay needs aligned transparent PNGs at the scene fps and a valid range"
                )
            if layer.mask:
                mask(layer.mask)
        return scene, canvas

    def save(self, scene, *, expected_revision, timing_seconds=None):
        scene = LofiScene.model_validate(scene)
        if timing_seconds:
            data = scene.model_dump(mode="json")
            overlays = {layer["id"]: layer for layer in data["overlays"]}
            for identity, value in timing_seconds.items():
                if identity not in overlays:
                    raise ValueError(f"unknown overlay timing: {identity}")
                timing = OverlaySeconds.model_validate(value)
                for field, seconds in (
                    ("repeat_frames", timing.repeat_seconds),
                    ("first_frame", timing.delay_seconds),
                ):
                    overlays[identity]["timing"][field] = round(
                        Fraction(str(seconds)) * scene.fps.num / scene.fps.den
                    )
            scene = LofiScene.model_validate(data)
        scene, _ = self.validate(scene)
        if scene.approval.status != "draft":
            raise ValueError("scene configuration saves cannot assert visual approval")
        return self.store.save_draft(scene, expected_revision=expected_revision)

    def template(self, scene):
        scene, canvas = self.validate(scene)
        digest = content_hash(scene.model_dump(mode="json", exclude={"approval", "revision"}))
        slots = [dict(id="master", z=0, kind="still", asset=scene.master)]
        for index, layer in enumerate(scene.scenery, 1):
            slots.append(
                dict(
                    id=f"scenery-{index}",
                    z=index,
                    kind="tile_strip",
                    asset=layer.asset,
                    mask=scene.window_mask,
                    tile_period=layer.repeat_width,
                    depth_factor=layer.depth,
                )
            )
        for index, layer in enumerate(scene.overlays, 1):
            slots.append(
                dict(
                    id=f"overlay-{index}",
                    z=len(slots),
                    kind="loop_overlay",
                    asset=layer.asset,
                    mask=layer.mask,
                    opacity=layer.opacity,
                    loop=layer.timing,
                )
            )
        template = SceneTemplate(
            schema_version="1.0",
            document_type="scene_template",
            id=f"lofi.{digest[:24]}",
            version="1.0",
            camera_id="lofi.fixed",
            design_canvas=canvas,
            capabilities=["lofi"],
            channels=[],
            anchors={},
            slots=slots,
            parameter_limits={"travel_speed": {"minimum": 0, "maximum": 1000}},
            mask_semantics="white_visible_black_hidden",
        )
        try:
            old = self.store.read(document_path(template))
        except FileNotFoundError:
            return self.store.save_draft(template, expected_revision=None)
        if not isinstance(old, SceneTemplate) or old.approval_hash != template.approval_hash:
            raise ValueError("saved scene configuration differs from its content identity")
        return old

    def create_video(self, request):
        request = CreateLofiVideo.model_validate(request)
        scene = self.scene(request.scene)
        if scene.revision != request.expected_scene_revision:
            raise RevisionConflict("scene changed; reload before creating this video")
        _, canvas = self.validate(scene)
        samples = sum(prepared_samples(self.assets.require_valid(ref)) for ref in request.music)
        if request.duration_seconds is None:
            if not samples:
                raise ValueError("choose music or provide a video duration")
            frames = ceil(Fraction(samples * scene.fps.num, 48000 * scene.fps.den))
        else:
            frames = round(Fraction(request.duration_seconds * scene.fps.num, scene.fps.den))
        if frames < 1 or Fraction(frames * scene.fps.den, scene.fps.num) > 21600:
            raise ValueError("video duration must be between one frame and six hours")
        if samples > scene.fps.sample_at(frames):
            raise ValueError("music exceeds video duration; choose Fit selected music")
        template = self.template(scene)
        episode = AuthoringService(self.assets).prepare_episode(
            NewEpisode(
                id=request.id,
                title=request.title,
                format="session",
                fps=scene.fps,
                canvas=canvas,
                duration_frames=frames,
                template=AssetRef(id=template.id, version=template.version),
                music=request.music,
            )
        )
        # NewEpisode prepares the standard silent/still schedule. The scene configuration adds
        # only a global travel curve; jobs/preview/audio retain their existing shared semantics.
        data = episode.model_dump(mode="json")
        data["curves"] = [
            dict(
                scope="episode",
                target="travel_speed",
                unit="design_px_per_second",
                interpolation="constant",
                limits={"minimum": 0, "maximum": 1000},
                keys=[{"frame": 0, "value": scene.speed}],
            )
        ]
        data["notes"] = (
            f"Lo-fi scene {scene.id}@{scene.version}; configuration {scene.approval_hash}"
        )
        configured = Episode.model_validate(data)
        ActionCompiler(self.assets).compile(configured)
        return self.store.save_draft(configured, expected_revision=None)
