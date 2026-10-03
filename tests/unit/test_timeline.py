import json
from fractions import Fraction

import pytest

from tabi.cli.main import main
from tabi.core.documents import parse_document
from tabi.core.models import Curve, Episode
from tabi.core.models.base import FrameInterval, FrameRate
from tabi.core.timeline import (
    CurveEvaluator,
    Timeline,
    TimelineError,
    contains,
    expand_random_actions,
    loop_frame,
)
from tabi.core.timeline.random import CounterRandom, prng_fingerprint


def curve(keys, *, interpolation="linear", outside="clamp", scope="episode"):
    return Curve.model_validate(
        {
            "scope": scope,
            "target": "travel_speed",
            "unit": "design_px_per_second",
            "interpolation": interpolation,
            "outside": outside,
            "limits": {"minimum": 0, "maximum": 120},
            "keys": [{"frame": frame, "value": value} for frame, value in keys],
        }
    )


def test_analytic_acceleration_stop_restart_and_out_of_order_queries():
    evaluator = CurveEvaluator(
        curve([(0, 0), (60, 60), (120, 0), (180, 0), (240, 120), (300, 120)]),
        FrameRate(num=30, den=1),
    )
    expected = {0: 0, 30: 15, 60: 60, 90: 105, 120: 120, 180: 120, 210: 150, 240: 240, 300: 480}
    for frame in [300, 0, 210, 60, 120, 240, 30, 180, 90]:
        assert evaluator.integral_at(frame) == expected[frame]
    for frame in range(301):
        assert evaluator.integral(0, frame) + evaluator.integral(frame, 300) == 480
    assert evaluator.value_at(150) == 0 and evaluator.value_at(210) == 60


def test_constant_speed_changes_do_not_jump_distance():
    evaluator = CurveEvaluator(
        curve([(0, 60), (90, 0), (150, 120), (300, 120)], interpolation="constant"),
        FrameRate(num=30, den=1),
    )
    assert [evaluator.integral_at(n) for n in [89, 90, 149, 150, 151, 300]] == [
        178,
        180,
        180,
        180,
        184,
        780,
    ]
    assert evaluator.value_at(90) == 0 and evaluator.value_at(150) == 120


def test_exact_rational_mapping_and_boundary_rounding():
    fps = FrameRate(num=30000, den=1001)
    evaluator = CurveEvaluator(curve([(0, 60)]), fps)
    assert evaluator.integral_at(1) == Fraction(1001, 500)
    assert fps.sample_at(30000) == 48048000
    # Ties-to-even at exact half samples, without float conversion.
    assert FrameRate(num=96000, den=1).sample_at(1) == 0
    assert FrameRate(num=96000, den=1).sample_at(3) == 2
    with pytest.raises(TimelineError):
        evaluator.integral_at(True)


@pytest.mark.parametrize("outside,expected", [("clamp", [30, 135, 360]), ("zero", [0, 75, 180])])
def test_curve_extrapolation_and_one_key(outside, expected):
    evaluator = CurveEvaluator(
        curve([(30, 60), (90, 120)], outside=outside), FrameRate(num=30, den=1)
    )
    assert [evaluator.integral_at(n) for n in [15, 60, 120]] == expected
    isolated = CurveEvaluator(curve([(30, 60)], outside="zero"), FrameRate(num=30, den=1))
    assert isolated.value_at(30) == 60 and isolated.value_at(31) == 0
    assert isolated.integral_at(120) == 0


def test_half_open_intervals_and_explicit_loop_origin():
    interval = FrameInterval(start_frame=3, end_frame=9)
    assert contains(interval, 3) and contains(interval, 8) and not contains(interval, 9)
    assert [loop_frame(n, 100, interval) for n in [100, 105, 106, 113]] == [3, 8, 3, 4]
    with pytest.raises(TimelineError):
        loop_frame(99, 100, interval)


def test_scoped_curves_override_episode_and_reject_duplicates(episode_data):
    episode_data.update(actions=[], tracks=[], curves=[curve([(0, 60)]).model_dump(mode="json")])
    scene = episode_data["scenes"][0]
    scene["curves"] = [curve([(0, 30)], scope=scene["id"]).model_dump(mode="json")]
    scene["initial_state"]["travel_distance_px"] = 100
    timeline = Timeline(Episode.model_validate(episode_data))
    assert timeline.travel_at(scene["id"], 30) == 130
    assert timeline.travel_at(scene["id"], 30, initial=Fraction(200)) == 230
    assert timeline.inspect(30)["audio_sample"] == 48000
    with pytest.raises(TimelineError, match="half-open"):
        timeline.active_scenes(episode_data["duration_frames"])
    episode_data["curves"].append(scene["curves"][0])
    with pytest.raises(TimelineError, match="duplicate"):
        Timeline(Episode.model_validate(episode_data))


def timing_episode(episode_data):
    episode_data.update(actions=[], tracks=[])
    scene_id = episode_data["scenes"][0]["id"]
    episode_data["random_actions"] = [
        {
            "id": "blink.test",
            "scene_id": scene_id,
            "pack": {"id": "pack.test", "version": "1.0"},
            "action_id": "blink",
            "version": "1.0",
            "channel": "face",
            "duration_frames": 6,
            "minimum_gap_frames": 30,
            "maximum_gap_frames": 90,
            "start_frame": 0,
            "end_frame": 600,
        }
    ]
    return Episode.model_validate(episode_data)


def test_deterministic_random_schedule_uses_whole_actions_and_inclusive_gaps(episode_data):
    episode = timing_episode(episode_data)
    schedule = expand_random_actions(episode)
    assert schedule == expand_random_actions(parse_document(episode.model_dump_json().encode()))
    assert schedule != expand_random_actions(episode.model_copy(update={"seed": episode.seed + 1}))
    previous = 0
    for action in schedule:
        assert 30 <= action.start_frame - previous <= 90
        assert action.end_frame - action.start_frame == 6 and action.end_frame <= 600
        previous = action.end_frame
    assert len(schedule) > 5
    assert len(prng_fingerprint().sha256) == 64


def test_random_conflicts_are_reported_instead_of_silently_removed(episode_data):
    episode = timing_episode(episode_data)
    first = expand_random_actions(episode)[0]
    episode = episode.model_copy(
        update={"actions": [first.model_copy(update={"id": "manual.blink"})]}
    )
    with pytest.raises(ValueError, match="overlapping"):
        expand_random_actions(episode)


def test_counter_reference_vector_and_identity_isolation():
    random = CounterRandom(42, "blink")
    # Frozen v1 vector independently calculated from literal JSON with OpenSSL SHA-256.
    assert [random.below(1000) for _ in range(5)] == [60, 789, 710, 903, 444]
    assert CounterRandom(42, "another.blink").below(1000) != 60


def test_cli_frame_inspection(episode_data, tmp_path, capsys):
    episode_data["curves"] = [curve([(0, 60)]).model_dump(mode="json")]
    path = tmp_path / "episode.json"
    path.write_text(json.dumps(episode_data))
    assert main(["timeline", "inspect", str(path), "--frame", "30"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["audio_sample"] == 48000
    assert result["scenes"][0]["travel_distance_px"] == 60
