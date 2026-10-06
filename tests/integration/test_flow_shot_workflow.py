"""The six-shot default uses real media and the same authenticated API as the browser."""

import pytest
from test_flow_workflow import exercise_90s_workflow

pytestmark = pytest.mark.media


def test_six_clean_starts_focused_retry_exact_cuts_reopen_and_continuous_soundtrack(tmp_path):
    exercise_90s_workflow(tmp_path, planned=True)
