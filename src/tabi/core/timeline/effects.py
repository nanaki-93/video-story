"""Validate prepared temporal effects independently of the render backend."""

from ..models.base import Canvas


def visible_canvas(asset):
    crop = asset.compatibility.crop
    return Canvas(width=crop.width, height=crop.height) if crop else asset.probe.canvas


def validate_effects(scene, template, timeline, resolve):
    targets = {slot.effect.strength_target for slot in template.slots if slot.effect}
    for slot in template.slots:
        if slot.loop is not None:
            source = resolve(scene.slot_assignments.get(slot.id, slot.asset), "asset")
            if (
                source.kind != "sequence"
                or visible_canvas(source) != template.design_canvas
                or source.probe.fps != timeline.episode.fps
                or source.probe.alpha_mode not in {"straight", "premultiplied"}
                or slot.loop.source.end_frame > source.probe.frame_count
            ):
                raise ValueError(
                    "loop overlay needs aligned transparent PNG frames and matching fps"
                )
            if slot.mask:
                mask = resolve(slot.mask, "asset")
                if mask.kind != "mask" or visible_canvas(mask) != template.design_canvas:
                    raise ValueError("loop overlay mask must match the scene canvas")
        effect = slot.effect
        if effect is None:
            continue
        curve = timeline.curve_for(scene.id, effect.strength_target)
        if curve and curve.curve.unit != "fraction":
            raise ValueError("effect strengths require fraction curves")
        limit = template.parameter_limits[effect.strength_target]
        if curve and any(not limit.minimum <= value <= limit.maximum for value in curve.values):
            raise ValueError("effect strength exceeds the template's reviewed capability limits")
        mask = resolve(slot.mask, "asset")
        if mask.kind != "mask" or visible_canvas(mask) != template.design_canvas:
            raise ValueError("effect mask must match the scene design canvas")
        ref = scene.slot_assignments.get(slot.id, slot.asset)
        if effect.kind == "tint":
            if ref is not None:
                raise ValueError("tint cannot be replaced by a media slot assignment")
            continue
        if ref is None:
            raise ValueError("prepared effect requires an explicit source asset")
        source = resolve(ref, "asset")
        if visible_canvas(source) != template.design_canvas or source.probe.alpha_mode not in {
            "straight",
            "premultiplied",
        }:
            raise ValueError("prepared effect needs scene-sized, explicit alpha artwork")
        if effect.loop is None:
            if source.kind != "still":
                raise ValueError("animated reflection needs an explicit prepared loop")
        elif (
            source.kind != "sequence"
            or source.probe.fps != timeline.episode.fps
            or effect.loop.end_frame > source.probe.frame_count
            or scene.initial_state.weather_phase_frame > scene.start_frame
        ):
            raise ValueError(
                "effect loop needs matching fps, valid PNG frames and a past global phase origin"
            )
    for scope, target in timeline.curves:
        if scope in {"episode", scene.id} and target != "travel_speed" and target not in targets:
            raise ValueError(f"curve {target} has no supported effect in scene {scene.id}")
