"""
PRAGYA AI — Shared Feature Pipeline  (v2)
==========================================
One function used identically for TRAINING and INFERENCE.
No train/serve mismatch. Includes strict temporal leakage check.

Key design decisions:
  - All rolling statistics are computed with respect to the passed-in
    `as_of_date`, so the function is safe to call at any historical date.
  - Outcome columns are stripped before any computation is done.
  - A hard assert fires if any source row has update_date > as_of_date.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from datetime import datetime
from typing import Optional

# ── Columns that must NEVER appear in the feature matrix ─────────────────────
OUTCOME_FIELDS = frozenset({
    "final_cost",
    "final_end_date",
    "delayed_flag",
    "overrun_flag",
    "implementation_risk_flag",
    "outcome_known_at",
    "is_anomaly_injection",
})

# ── Feature-set definition (canonical, ordered) ───────────────────────────────
CATEGORICAL_FEATURES: list[str] = [
    "sector", "ministry", "agency", "state", "project_type",
]

NUMERIC_FEATURES: list[str] = [
    # Progress
    "progress_gap",
    "progress_velocity_1",       # delta over last 1 update
    "progress_velocity_3",       # mean over last 3 updates
    "velocity_needed_to_finish",
    # Milestones
    "max_milestone_delay_months",
    "pct_milestones_delayed",
    # Cost
    "cost_growth_pct",
    "expenditure_to_progress_ratio",
    "burn_rate",
    # Update-cadence
    "days_since_last_update",
    "avg_update_gap",
    "count_of_revised_dates",
    # Missingness
    "missing_velocity_flag",
]

ALL_FEATURES: list[str] = CATEGORICAL_FEATURES + NUMERIC_FEATURES

# Feature-set version — bump when schema changes
FEATURE_SET_VERSION = "v2"


# ── Main entry point ──────────────────────────────────────────────────────────

def compute_features(
    df_history: pd.DataFrame,
    as_of_date: str,
    *,
    assert_no_outcome_fields: bool = True,
) -> pd.DataFrame:
    """
    Compute features for every project in *df_history* using ONLY data
    valid on or before `as_of_date`.

    Parameters
    ----------
    df_history : DataFrame
        All historical project-update rows (may contain multiple projects).
    as_of_date : str
        ISO-8601 date string (YYYY-MM-DD). Rows after this date will raise.
    assert_no_outcome_fields : bool
        If True (default), outcome columns are stripped before features are
        computed and a warning is issued.

    Returns
    -------
    DataFrame indexed by project_id, columns = ALL_FEATURES.

    Raises
    ------
    AssertionError
        If any row has update_date > as_of_date (temporal leakage detected).
    """
    df = df_history.copy()
    as_of = pd.to_datetime(as_of_date)

    # ── 1. Strip outcome fields ───────────────────────────────────────────────
    if assert_no_outcome_fields:
        leaked = OUTCOME_FIELDS.intersection(df.columns)
        if leaked:
            df = df.drop(columns=list(leaked), errors="ignore")

    # ── 2. Parse dates ────────────────────────────────────────────────────────
    date_cols = [
        "update_date", "planned_start", "planned_end",
        "expected_completion_date",
        "milestone_planned_date", "milestone_expected_date", "milestone_actual_date",
    ]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # ── 3. TEMPORAL LEAKAGE CHECK ─────────────────────────────────────────────
    #   Every row's update_date must be ≤ as_of_date.
    future_mask = df["update_date"] > as_of
    if future_mask.any():
        bad = df.loc[future_mask, "update_date"].dt.strftime("%Y-%m-%d").unique()[:5]
        raise AssertionError(
            f"LEAKAGE DETECTED: {future_mask.sum()} rows have update_date "
            f"after as_of_date {as_of_date}. Sample future dates: {list(bad)}"
        )

    # ── 4. Sort chronologically per project ───────────────────────────────────
    df = df.sort_values(["project_id", "update_date"]).reset_index(drop=True)

    # ── 5. Rolling / lag features (computed before taking latest snapshot) ────
    grp = df.groupby("project_id", sort=False)

    df["prev_physical_1"]    = grp["physical_progress_pct"].shift(1)
    df["prev_physical_3"]    = grp["physical_progress_pct"].shift(3)
    df["prev_update_date"]   = grp["update_date"].shift(1)

    df["days_since_last_update"] = (
        (df["update_date"] - df["prev_update_date"]).dt.days.clip(lower=0)
    )
    df["progress_velocity_1"] = (
        df["physical_progress_pct"] - df["prev_physical_1"]
    )
    df["progress_velocity_3"] = (
        (df["physical_progress_pct"] - df["prev_physical_3"]) / 3.0
    )

    # Running mean of update gap (cadence proxy)
    df["avg_update_gap"] = grp["days_since_last_update"].transform("mean")

    # Count of times expected_completion was revised beyond planned_end
    df["date_was_revised"] = (
        df["expected_completion_date"] > df["planned_end"]
    ).astype(int)
    df["count_of_revised_dates"] = grp["date_was_revised"].cumsum()

    # ── 6. Take the latest snapshot per project ───────────────────────────────
    # Using sort + drop_duplicates to avoid multi-index issues with groupby.apply
    latest = (
        df.sort_values(["project_id", "update_date"])
          .drop_duplicates(subset="project_id", keep="last")
          .copy()
          .reset_index(drop=True)
    )

    # ── 7. Time-based expected progress (linear plan) ─────────────────────────
    latest["total_planned_days"] = (
        (latest["planned_end"] - latest["planned_start"]).dt.days
    ).clip(lower=1)

    latest["days_elapsed"] = (
        (latest["update_date"] - latest["planned_start"]).dt.days
    ).clip(lower=0)

    latest["expected_progress"] = (
        (latest["days_elapsed"] / latest["total_planned_days"]) * 100
    ).clip(0, 100)

    # ── 8. Feature: progress_gap ──────────────────────────────────────────────
    latest["progress_gap"] = (
        latest["expected_progress"] - latest["physical_progress_pct"]
    )

    # ── 9. Feature: velocity_needed_to_finish ─────────────────────────────────
    latest["days_remaining_planned"] = (
        (latest["planned_end"] - latest["update_date"]).dt.days
    )
    latest["progress_remaining"] = (
        100.0 - latest["physical_progress_pct"].clip(0, 100)
    )
    latest["velocity_needed_to_finish"] = np.where(
        latest["days_remaining_planned"] > 0,
        latest["progress_remaining"] / latest["days_remaining_planned"],
        999.0,   # past the deadline and still incomplete → very high risk
    )

    # ── 10. Milestone delay features ─────────────────────────────────────────
    m_planned  = latest["milestone_planned_date"]
    m_actual   = latest["milestone_actual_date"]
    m_expected = latest["milestone_expected_date"]

    # If the milestone was completed, use actual delay; otherwise, use expected
    actual_delay   = (m_actual  - m_planned).dt.days.fillna(0).clip(lower=0)
    expected_delay = np.where(
        m_actual.isna(),
        (m_expected - m_planned).dt.days.clip(lower=0).fillna(0),
        0,
    )
    latest["max_milestone_delay_months"] = (
        np.maximum(actual_delay, expected_delay) / 30.0
    )
    latest["pct_milestones_delayed"] = (
        (latest["max_milestone_delay_months"] > 0).astype(float)
    )

    # ── 11. Cost features ─────────────────────────────────────────────────────
    sc = latest["sanctioned_cost"].replace(0, np.nan)

    latest["cost_growth_pct"] = (
        (latest["revised_cost"] - latest["sanctioned_cost"]) / sc * 100
    ).fillna(0.0)

    phys_frac = (latest["physical_progress_pct"] / 100.0).replace(0, np.nan)
    baseline_spend = phys_frac * sc
    latest["expenditure_to_progress_ratio"] = (
        latest["cumulative_expenditure"] / baseline_spend
    ).fillna(1.0).clip(0, 10)

    elapsed_frac = (latest["days_elapsed"] / latest["total_planned_days"]).replace(0, np.nan)
    latest["burn_rate"] = (
        latest["cumulative_expenditure"] / (elapsed_frac * sc)
    ).fillna(1.0).clip(0, 10)

    # ── 12. Impute & fill ─────────────────────────────────────────────────────
    latest["progress_velocity_1"]    = latest["progress_velocity_1"].fillna(0.0)
    latest["progress_velocity_3"]    = latest["progress_velocity_3"].fillna(0.0)
    latest["days_since_last_update"] = latest["days_since_last_update"].fillna(0.0)
    latest["avg_update_gap"]         = latest["avg_update_gap"].fillna(0.0)
    latest["count_of_revised_dates"] = latest["count_of_revised_dates"].fillna(0).astype(int)

    # ── 13. Missingness indicator ─────────────────────────────────────────────
    latest["missing_velocity_flag"] = latest["prev_physical_1"].isna().astype(int)

    # ── 14. Return only the canonical feature columns ─────────────────────────
    result = latest.set_index("project_id")[ALL_FEATURES]
    return result


def get_feature_names() -> list[str]:
    """Return the canonical ordered list of ALL feature names."""
    return ALL_FEATURES.copy()


def get_feature_set_version() -> str:
    """Return the current feature-set version string."""
    return FEATURE_SET_VERSION
