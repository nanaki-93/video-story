from types import SimpleNamespace

import pytest

from tabi.core.flow.review import FlowReview, difference, repeated_ranges
from tabi.core.flow.service import FlowError
from tabi.core.models.base import FrameInterval


def test_repeated_ranges_are_exact_half_open_intervals():
    assert repeated_ranges([b"a", b"b", b"b", b"b", b"c"], minimum=3) == [
        {"start_frame": 1, "end_frame": 4}
    ]
    assert repeated_ranges([b"a", b"b"], minimum=2) == []
    assert repeated_ranges([b"a"] * 3, minimum=3) == [{"start_frame": 0, "end_frame": 3}]


def test_difference_is_advisory_not_a_boolean_approval():
    assert difference(bytes([0, 10]), bytes([10, 0])) == 10


def test_section_does_not_create_a_false_native_extension_parent():
    candidate = SimpleNamespace(
        review="pending",
        media=SimpleNamespace(sha256="source"),
        parent_id="parent",
        attempt_id="attempt",
        frame_count=192,
        trim=FrameInterval(start_frame=0, end_frame=192),
    )
    attempt = SimpleNamespace(id="attempt", mode="extend")
    episode = SimpleNamespace(
        accepted_ids=["parent"],
        attempts=[attempt],
        recipe=SimpleNamespace(shots=[], target_frames=2160),
        accepted_frames=192,
    )
    validate = FlowReview._validate_section
    with pytest.raises(FlowError, match="opening of a continuation"):
        validate(episode, candidate, FrameInterval(start_frame=24, end_frame=192), "source")
    with pytest.raises(FlowError, match="source ending"):
        validate(episode, candidate, FrameInterval(start_frame=0, end_frame=168), "source")
    with pytest.raises(FlowError, match="decoded source"):
        validate(episode, candidate, FrameInterval(start_frame=0, end_frame=193), "source")
    attempt.mode = "shot_start"
    validate(episode, candidate, FrameInterval(start_frame=24, end_frame=192), "source")
    episode.accepted_ids = []
    with pytest.raises(FlowError, match="old branch"):
        validate(episode, candidate, FrameInterval(start_frame=24, end_frame=192), "source")
