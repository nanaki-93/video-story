"""Exact piecewise integration, independent of playback order and chunk boundaries."""

from bisect import bisect_right
from fractions import Fraction

from ..models import Curve, Episode
from ..models.base import FrameInterval, FrameRate


class TimelineError(ValueError):
    pass


def frame_number(frame: int) -> int:
    if type(frame) is not int or frame < 0:
        raise TimelineError("frame must be a nonnegative integer")
    return frame


def contains(interval: FrameInterval, frame: int) -> bool:
    return interval.start_frame <= frame_number(frame) < interval.end_frame


def loop_frame(frame: int, origin: int, loop: FrameInterval) -> int:
    frame_number(frame)
    frame_number(origin)
    if frame < origin:
        raise TimelineError("frame precedes the clip phase origin")
    return loop.start_frame + (frame - origin) % (loop.end_frame - loop.start_frame)


class CurveEvaluator:
    def __init__(self, curve: Curve, fps: FrameRate):
        self.curve = Curve.model_validate(curve)
        self.fps = FrameRate.model_validate(fps)
        self.frames = [key.frame for key in self.curve.keys]
        # Decimal JSON values become exact rationals; never accumulate binary float steps.
        self.values = [Fraction(str(key.value)) for key in self.curve.keys]
        initial = self.values[0] * self.frames[0] if curve.outside == "clamp" else Fraction(0)
        self.prefix = [initial]
        for index in range(1, len(self.frames)):
            length = self.frames[index] - self.frames[index - 1]
            area = self.values[index - 1] * length
            if curve.interpolation == "linear":
                area = (self.values[index - 1] + self.values[index]) * Fraction(length, 2)
            self.prefix.append(self.prefix[-1] + area)

    def value_at(self, frame: int) -> Fraction:
        frame_number(frame)
        index = bisect_right(self.frames, frame) - 1
        if index < 0:
            return self.values[0] if self.curve.outside == "clamp" else Fraction(0)
        if frame > self.frames[-1]:
            return self.values[-1] if self.curve.outside == "clamp" else Fraction(0)
        if self.curve.interpolation == "constant" or index == len(self.frames) - 1:
            return self.values[index]
        part = Fraction(frame - self.frames[index], self.frames[index + 1] - self.frames[index])
        return self.values[index] + part * (self.values[index + 1] - self.values[index])

    def integral_at(self, frame: int) -> Fraction:
        """Integral from global frame boundary 0 to frame, in value × seconds."""
        frame_number(frame)
        index = bisect_right(self.frames, frame) - 1
        if index < 0:
            area = self.values[0] * frame if self.curve.outside == "clamp" else Fraction(0)
        else:
            area = self.prefix[index]
            length = frame - self.frames[index]
            if index == len(self.frames) - 1:
                if self.curve.outside == "clamp":
                    area += self.values[index] * length
            else:
                area += self.values[index] * length
                if self.curve.interpolation == "linear":
                    slope = (self.values[index + 1] - self.values[index]) / (
                        self.frames[index + 1] - self.frames[index]
                    )
                    area += slope * length * length / 2
        return area * Fraction(self.fps.den, self.fps.num)

    def integral(self, start: int, end: int) -> Fraction:
        if frame_number(end) < frame_number(start):
            raise TimelineError("integration end precedes start")
        return self.integral_at(end) - self.integral_at(start)


class Timeline:
    def __init__(self, episode: Episode):
        self.episode = Episode.model_validate(episode)
        self.scenes = {scene.id: scene for scene in episode.scenes}
        self.curves = {}
        for curve in [
            *episode.curves,
            *(curve for scene in episode.scenes for curve in scene.curves),
        ]:
            key = (curve.scope, curve.target)
            if key in self.curves:
                raise TimelineError(f"duplicate curve for {curve.scope}.{curve.target}")
            if curve.target == "travel_speed" and curve.unit != "design_px_per_second":
                raise TimelineError("travel_speed requires design_px_per_second")
            self.curves[key] = CurveEvaluator(curve, episode.fps)

    def active_scenes(self, frame: int) -> list[str]:
        if frame_number(frame) >= self.episode.duration_frames:
            raise TimelineError("frame is outside the episode's half-open interval")
        return [scene.id for scene in self.episode.scenes if contains(scene, frame)]

    def curve_for(self, scene_id: str, target: str) -> CurveEvaluator | None:
        if scene_id not in self.scenes:
            raise TimelineError(f"unknown scene: {scene_id}")
        return self.curves.get((scene_id, target), self.curves.get(("episode", target)))

    def value_at(self, scene_id: str, target: str, frame: int, *, default: float = 0) -> Fraction:
        self._in_scene(scene_id, frame)
        curve = self.curve_for(scene_id, target)
        return curve.value_at(frame) if curve else Fraction(str(default))

    def _in_scene(self, scene_id: str, frame: int) -> None:
        frame_number(frame)
        scene = self.scenes.get(scene_id)
        # The end boundary is useful for integrating the final state's distance.
        if scene is None or not scene.start_frame <= frame <= scene.end_frame:
            raise TimelineError("frame is outside the requested scene")

    def travel_at(self, scene_id: str, frame: int, *, initial: Fraction | None = None) -> Fraction:
        self._in_scene(scene_id, frame)
        scene = self.scenes[scene_id]
        curve = self.curve_for(scene_id, "travel_speed")
        base = Fraction(str(scene.initial_state.travel_distance_px)) if initial is None else initial
        return base + (curve.integral(scene.start_frame, frame) if curve else 0)

    def inspect(self, frame: int) -> dict:
        targets = sorted({target for _, target in self.curves})
        seconds = Fraction(frame_number(frame) * self.episode.fps.den, self.episode.fps.num)
        return {
            "frame": frame,
            "time_seconds": {"num": seconds.numerator, "den": seconds.denominator},
            "audio_sample": self.episode.fps.sample_at(frame),
            "scenes": [
                {
                    "id": scene_id,
                    "travel_distance_px": float(self.travel_at(scene_id, frame)),
                    "parameters": {
                        target: float(self.value_at(scene_id, target, frame)) for target in targets
                    },
                }
                for scene_id in self.active_scenes(frame)
            ],
        }
