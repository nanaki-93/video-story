"""Independent cuts and saved extensions use actual media and authenticated services."""

import pytest
from test_flow_workflow import exercise_90s_workflow

pytestmark = pytest.mark.media


def test_twelve_independent_starts_fixed_cuts_reopen_and_continuous_soundtrack(tmp_path):
    exercise_90s_workflow(tmp_path, planned=True)


def test_saved_six_shot_recipe_keeps_native_extensions_and_exact_export(tmp_path):
    exercise_90s_workflow(tmp_path, planned=True, legacy_planned=True)
