import runpy
from pathlib import Path

import pytest

byte_range = runpy.run_path(
    str(Path(__file__).resolve().parents[2] / "scripts/web_playback_spike.py")
)["byte_range"]


def test_browser_ranges_cover_closed_open_suffix_and_clamped_requests():
    assert byte_range(None, 100) == (0, 100)
    assert byte_range("bytes=0-1", 100) == (0, 2)
    assert byte_range("bytes=90-", 100) == (90, 100)
    assert byte_range("bytes=-10", 100) == (90, 100)
    assert byte_range("bytes=90-1000", 100) == (90, 100)
    assert byte_range("bytes=-1000", 100) == (0, 100)


def test_browser_ranges_reject_unsatisfied_and_multiple_requests():
    for header in ("bytes=100-", "bytes=4-3", "bytes=-0", "bytes=-", "bytes=0-1,3-4"):
        with pytest.raises(ValueError):
            byte_range(header, 100)
