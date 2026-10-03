"""FFmpeg expressions derived from the shared exact integral, never local elapsed speed."""

from fractions import Fraction

from ..timeline import Timeline


def number(value: Fraction | int | float) -> str:
    value = value if isinstance(value, Fraction) else Fraction(str(value))
    return (
        str(value.numerator)
        if value.denominator == 1
        else f"({value.numerator}/{value.denominator})"
    )


def value_expression(timeline, scene_id, target, frame, *, default=0):
    curve = timeline.curve_for(scene_id, target)
    if curve is None:
        return number(default)
    result = number(curve.values[-1])
    if curve.curve.outside == "zero":
        result = f"if(eq({frame},{curve.frames[-1]}),{result},0)"
    for index in reversed(range(len(curve.frames) - 1)):
        value = number(curve.values[index])
        if curve.curve.interpolation == "linear":
            slope = (curve.values[index + 1] - curve.values[index]) / (
                curve.frames[index + 1] - curve.frames[index]
            )
            value += f"+{number(slope)}*({frame}-{curve.frames[index]})"
        result = f"if(lt({frame},{curve.frames[index + 1]}),({value}),{result})"
    before = number(curve.values[0]) if curve.curve.outside == "clamp" else "0"
    return f"if(lt({frame},{curve.frames[0]}),{before},{result})"


def distance_expression(timeline: Timeline, scene_id: str, frame: str) -> str:
    scene = timeline.scenes[scene_id]
    curve = timeline.curve_for(scene_id, "travel_speed")
    initial = Fraction(str(scene.initial_state.travel_distance_px))
    if curve is None:
        return number(initial)
    tail = number(curve.prefix[-1])
    if curve.curve.outside == "clamp":
        tail += f"+{number(curve.values[-1])}*({frame}-{curve.frames[-1]})"
    result = f"({tail})"
    for i in reversed(range(len(curve.frames) - 1)):
        elapsed = f"({frame}-{curve.frames[i]})"
        area = f"{number(curve.prefix[i])}+{number(curve.values[i])}*{elapsed}"
        if curve.curve.interpolation == "linear":
            half_slope = (curve.values[i + 1] - curve.values[i]) / (
                2 * (curve.frames[i + 1] - curve.frames[i])
            )
            area += f"+{number(half_slope)}*{elapsed}*{elapsed}"
        result = f"if(lt({frame},{curve.frames[i + 1]}),({area}),{result})"
    before = f"{number(curve.values[0])}*{frame}" if curve.curve.outside == "clamp" else "0"
    result = f"if(lt({frame},{curve.frames[0]}),({before}),{result})"
    origin = initial - curve.integral_at(scene.start_frame)
    return f"({number(origin)}+({result})*{curve.fps.den}/{curve.fps.num})"
