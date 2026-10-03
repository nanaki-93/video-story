"""Bounded FFmpeg expressions from the shared global-time integral."""

from bisect import bisect_right
from fractions import Fraction

from ..timeline import Timeline


def number(value: Fraction | int | float) -> str:
    value = value if isinstance(value, Fraction) else Fraction(str(value))
    return (
        str(value.numerator)
        if value.denominator == 1
        else f"({value.numerator}/{value.denominator})"
    )


def piecewise(frames, values, frame, first, end):
    """Discard unreachable branches, then balance dense curves to bound parser depth.

    Values still contain global frame offsets and integral prefixes. Selecting a
    render interval must never rebase travel or effect phase to the chunk start.
    """
    left = 0 if first is None else bisect_right(frames, first)
    right = len(frames) if end is None else bisect_right(frames, end - 1)

    def branch(lo, hi):
        if lo == hi:
            return f"({values[lo]})"
        middle = (lo + hi) // 2
        return f"if(lt({frame},{frames[middle]}),{branch(lo, middle)},{branch(middle + 1, hi)})"

    return branch(left, right)


def value_expression(
    timeline, scene_id, target, frame, *, default=0, first_frame=None, end_frame=None
):
    curve = timeline.curve_for(scene_id, target)
    if curve is None:
        return number(default)
    before = number(curve.values[0]) if curve.curve.outside == "clamp" else "0"
    values = [before]
    for index in range(len(curve.frames) - 1):
        value = number(curve.values[index])
        if curve.curve.interpolation == "linear":
            slope = (curve.values[index + 1] - curve.values[index]) / (
                curve.frames[index + 1] - curve.frames[index]
            )
            value += f"+{number(slope)}*({frame}-{curve.frames[index]})"
        values.append(value)
    tail = number(curve.values[-1])
    if curve.curve.outside == "zero":
        tail = f"if(eq({frame},{curve.frames[-1]}),{tail},0)"
    values.append(tail)
    return piecewise(curve.frames, values, frame, first_frame, end_frame)


def distance_expression(
    timeline: Timeline, scene_id: str, frame: str, *, first_frame=None, end_frame=None
) -> str:
    scene = timeline.scenes[scene_id]
    curve = timeline.curve_for(scene_id, "travel_speed")
    initial = Fraction(str(scene.initial_state.travel_distance_px))
    if curve is None:
        return number(initial)
    before = f"{number(curve.values[0])}*{frame}" if curve.curve.outside == "clamp" else "0"
    values = [before]
    for i in range(len(curve.frames) - 1):
        elapsed = f"({frame}-{curve.frames[i]})"
        area = f"{number(curve.prefix[i])}+{number(curve.values[i])}*{elapsed}"
        if curve.curve.interpolation == "linear":
            half_slope = (curve.values[i + 1] - curve.values[i]) / (
                2 * (curve.frames[i + 1] - curve.frames[i])
            )
            area += f"+{number(half_slope)}*{elapsed}*{elapsed}"
        values.append(area)
    tail = number(curve.prefix[-1])
    if curve.curve.outside == "clamp":
        tail += f"+{number(curve.values[-1])}*({frame}-{curve.frames[-1]})"
    values.append(tail)
    result = piecewise(curve.frames, values, frame, first_frame, end_frame)
    origin = initial - curve.integral_at(scene.start_frame)
    return f"({number(origin)}+({result})*{curve.fps.den}/{curve.fps.num})"
