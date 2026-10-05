from tabi.core.flow.review import difference, repeated_ranges


def test_repeated_ranges_are_exact_half_open_intervals():
    assert repeated_ranges([b"a", b"b", b"b", b"b", b"c"], minimum=3) == [
        {"start_frame": 1, "end_frame": 4}
    ]
    assert repeated_ranges([b"a", b"b"], minimum=2) == []
    assert repeated_ranges([b"a"] * 3, minimum=3) == [{"start_frame": 0, "end_frame": 3}]


def test_difference_is_advisory_not_a_boolean_approval():
    assert difference(bytes([0, 10]), bytes([10, 0])) == 10
