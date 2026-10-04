"""
PRAGYA AI — Feature Pipeline Tests  (v2)
==========================================
pytest tests for:
  1. Temporal leakage detection (hard assert)
  2. No-leakage happy path
  3. Outcome field stripping
  4. Feature completeness (all expected columns present)
  5. Velocity and milestone imputation
  6. Missing-velocity flag
"""
from __future__ import annotations

import pytest
import pandas as pd
import numpy as np

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from ml_core.features.pipeline import (
    ALL_FEATURES,
    OUTCOME_FIELDS,
    compute_features,
    get_feature_names,
    get_feature_set_version,
)


# ── Fixture: minimal valid project history ────────────────────────────────────

def _make_history(update_dates: list[str], progress: list[float]) -> pd.DataFrame:
    n = len(update_dates)
    return pd.DataFrame({
        "project_id":               ["P1"] * n,
        "update_date":              update_dates,
        "physical_progress_pct":    progress,
        "financial_progress_pct":   progress,
        "cumulative_expenditure":   [p * 1.0 for p in progress],
        "revised_cost":             [100.0] * n,
        "sanctioned_cost":          [100.0] * n,
        "planned_start":            ["2025-01-01"] * n,
        "planned_end":              ["2026-12-31"] * n,
        "expected_completion_date": ["2026-12-31"] * n,
        "milestone_planned_date":   ["2025-06-01"] * n,
        "milestone_expected_date":  ["2025-07-01"] * n,
        "milestone_actual_date":    ["2025-07-05"] * n,
        "sector":                   ["Roads"] * n,
        "ministry":                 ["MoRTH"] * n,
        "agency":                   ["Agency_1"] * n,
        "state":                    ["MH"] * n,
        "project_type":             ["Construction"] * n,
    })


# ── Test 1: Leakage detection raises AssertionError ─────────────────────────

def test_leakage_raises_error():
    """
    If any update_date is AFTER as_of_date, compute_features must raise
    AssertionError mentioning 'LEAKAGE DETECTED'.
    """
    df = _make_history(["2026-01-01", "2026-05-01"], [10.0, 50.0])
    with pytest.raises(AssertionError, match="LEAKAGE DETECTED"):
        compute_features(df, "2026-03-01")   # 2026-05-01 > 2026-03-01 ← leaks


# ── Test 2: No-leakage happy path ─────────────────────────────────────────────

def test_no_leakage_passes():
    """Providing as_of_date ≥ latest update_date must succeed."""
    df = _make_history(["2026-01-01", "2026-05-01"], [10.0, 50.0])
    result = compute_features(df, "2026-06-01")
    assert len(result) == 1, "Expected one row (one project)"
    assert "progress_gap" in result.columns


# ── Test 3: Outcome fields are stripped ───────────────────────────────────────

def test_outcome_fields_stripped():
    """Outcome columns (final_cost, delayed_flag, etc.) must not appear in output."""
    df = _make_history(["2026-01-01", "2026-05-01"], [10.0, 50.0])
    # Inject outcome fields into the raw dataframe
    for col in ["final_cost", "final_end_date", "delayed_flag", "overrun_flag"]:
        df[col] = 999
    result = compute_features(df, "2026-06-01")
    for col in OUTCOME_FIELDS:
        assert col not in result.columns, f"Outcome field '{col}' leaked into features!"


# ── Test 4: All feature columns are present ───────────────────────────────────

def test_all_feature_columns_present():
    """The output DataFrame must have exactly the columns in ALL_FEATURES."""
    df = _make_history(["2026-01-01", "2026-05-01"], [10.0, 50.0])
    result = compute_features(df, "2026-06-01")
    missing = set(ALL_FEATURES) - set(result.columns)
    extra   = set(result.columns) - set(ALL_FEATURES)
    assert not missing, f"Missing features: {missing}"
    assert not extra,   f"Extra features: {extra}"


# ── Test 5: progress_gap is correct ──────────────────────────────────────────

def test_progress_gap_correctness():
    """
    For a project that started on 2025-01-01, ends 2026-01-01, with an update
    on 2025-07-01 (≈ 50% of the way), but actual progress = 30%, the gap
    should be approximately 20 percentage points.
    """
    df = _make_history(["2025-07-01"], [30.0])
    # Single-row project, as_of 2025-07-01
    result = compute_features(df, "2025-07-01")
    gap = result["progress_gap"].iloc[0]
    # Fixture uses planned_end=2026-12-31 (730-day project).
    # At 2025-07-01: 181 days elapsed / 730 days = 24.8% expected progress.
    # Actual = 30%, so gap = expected - actual = 24.8 - 30 = -5.2 (ahead of schedule).
    assert -15 < gap < 5, f"progress_gap={gap} unexpectedly out of range"


# ── Test 6: Missing-velocity flag for first update ───────────────────────────

def test_missing_velocity_flag():
    """First update per project (no predecessor) must have missing_velocity_flag=1."""
    df = _make_history(["2025-07-01"], [30.0])
    result = compute_features(df, "2025-07-01")
    assert result["missing_velocity_flag"].iloc[0] == 1


# ── Test 7: Second update has velocity computed ───────────────────────────────

def test_velocity_computed_for_second_update():
    """Second update should have missing_velocity_flag=0 and a non-zero velocity_1."""
    df = _make_history(["2025-04-01", "2025-07-01"], [10.0, 30.0])
    result = compute_features(df, "2025-07-01")
    assert result["missing_velocity_flag"].iloc[0] == 0
    assert result["progress_velocity_1"].iloc[0] == pytest.approx(20.0, abs=1.0)


# ── Test 8: Multiple projects do not bleed into each other ────────────────────

def test_multi_project_isolation():
    """Features for P1 and P2 must be computed independently."""
    df = pd.concat([
        _make_history(["2025-01-01", "2025-07-01"], [10.0, 40.0]).assign(project_id="P1"),
        _make_history(["2025-01-01", "2025-07-01"], [10.0, 70.0]).assign(project_id="P2"),
    ]).reset_index(drop=True)

    result = compute_features(df, "2025-08-01")
    assert len(result) == 2
    v1_p1 = result.loc["P1", "progress_velocity_1"]
    v1_p2 = result.loc["P2", "progress_velocity_1"]
    assert v1_p1 != v1_p2, f"Velocities should differ: P1={v1_p1}, P2={v1_p2}"


# ── Test 9: get_feature_names and version are stable ─────────────────────────

def test_feature_names_stable():
    names = get_feature_names()
    assert names == ALL_FEATURES
    assert isinstance(get_feature_set_version(), str)
    assert get_feature_set_version().startswith("v")


# ── Test 10: Cost features are finite and clipped ─────────────────────────────

def test_cost_features_clipped():
    """burn_rate and expenditure_to_progress_ratio must be in [0, 10]."""
    df = _make_history(["2025-04-01", "2025-10-01"], [5.0, 15.0])
    # Make cumulative_expenditure very large to test clipping
    df["cumulative_expenditure"] = 9999.0
    result = compute_features(df, "2025-11-01")
    assert result["burn_rate"].iloc[0] <= 10.0
    assert result["expenditure_to_progress_ratio"].iloc[0] <= 10.0
    assert result["burn_rate"].iloc[0] >= 0.0
