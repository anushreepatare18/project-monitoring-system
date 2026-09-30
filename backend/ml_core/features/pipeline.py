"""
PRAGYA AI — Shared Feature Engineering Pipeline (Task 1)

One function, compute_features(), used identically for training AND inference.
Includes automated leakage checks, missingness flags, and all velocity/cost/
milestone/update-gap features specified in the SRS.

Usage:
    from backend.ml_core.features.pipeline import compute_features, build_training_dataset
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

# ── Feature column groups ──────────────────────────────────────────────────────
NUMERIC_FEATURES: List[str] = [
    "progress_gap",
    "velocity_last_1",
    "velocity_last_3",
    "velocity_last_6",
    "velocity_needed_to_finish",
    "pct_milestones_delayed",
    "max_milestone_delay_months",
    "cost_growth_pct",
    "expenditure_to_progress_ratio",
    "burn_rate_per_day",
    "days_since_last_update",
    "avg_update_gap",
    "count_of_revised_dates",
    "project_age_days",
    "planned_duration_days",
    "n_updates_so_far",
]

CATEGORICAL_FEATURES: List[str] = ["sector", "ministry", "agency"]

MISSINGNESS_FLAGS: List[str] = [
    "physical_progress_pct_missing",
    "cumulative_expenditure_missing",
    "revised_cost_missing",
    "milestone_data_missing",
    "expected_completion_date_missing",
]

ALL_FEATURES: List[str] = NUMERIC_FEATURES + CATEGORICAL_FEATURES + MISSINGNESS_FLAGS

# Sector-level cost overrun tolerances
SECTOR_COST_TOLERANCE: Dict[str, float] = {
    "Highways": 0.15,
    "Railways": 0.12,
    "Power Generation": 0.10,
    "Default": 0.10,
}


# ── Core leakage-safe feature computation ─────────────────────────────────────

def compute_features(
    project_df: pd.DataFrame,
    as_of_date: str,
) -> Optional[Dict[str, Any]]:
    """
    Compute all risk-prediction features for one project as of *as_of_date*.

    Parameters
    ----------
    project_df : pd.DataFrame
        ALL updates for a SINGLE project.  May contain dates *after* as_of_date
        iff they were accidentally included by the caller — the leakage check
        will raise if any such rows exist.
    as_of_date : str
        ISO date string 'YYYY-MM-DD'.  Only data on/before this date is used.

    Returns
    -------
    dict | None
        Feature dictionary, or None if no data exists before as_of_date.

    Raises
    ------
    ValueError
        Immediately if any row's update_date > as_of_date (leakage guard).
    """
    as_of = pd.Timestamp(as_of_date)

    # ── LEAKAGE CHECK ────────────────────────────────────────────────────────
    project_df = project_df.copy()
    project_df["update_date"] = pd.to_datetime(project_df["update_date"])

    future_rows = project_df[project_df["update_date"] > as_of]
    if not future_rows.empty:
        bad_dates = future_rows["update_date"].dt.date.tolist()
        raise ValueError(
            f"[LEAKAGE] {len(future_rows)} row(s) with update_date after "
            f"as_of_date={as_of_date}: {bad_dates[:5]}"
        )

    # ── Filter & sort ────────────────────────────────────────────────────────
    df = project_df[project_df["update_date"] <= as_of].sort_values("update_date").reset_index(drop=True)

    if df.empty:
        return None

    latest = df.iloc[-1]
    features: Dict[str, Any] = {}
    flags: Dict[str, int] = {f: 0 for f in MISSINGNESS_FLAGS}

    # ── Helper: safe scalar extraction ──────────────────────────────────────
    def _get(col: str, default: float = 0.0) -> float:
        val = latest.get(col)
        if val is None or (isinstance(val, float) and np.isnan(val)):
            flags[f"{col}_missing"] = 1
            return default
        try:
            return float(val)
        except (TypeError, ValueError):
            flags[f"{col}_missing"] = 1
            return default

    # ── Raw scalars ──────────────────────────────────────────────────────────
    actual_progress = _get("physical_progress_pct", 0.0)
    sanctioned_cost = max(_get("sanctioned_cost", 1.0), 1.0)  # guard ÷0
    cum_expenditure = _get("cumulative_expenditure", 0.0)
    revised_cost    = _get("revised_cost", sanctioned_cost)

    # ── Dates ────────────────────────────────────────────────────────────────
    planned_start = pd.Timestamp(latest["planned_start"])
    planned_end   = pd.Timestamp(latest["planned_end"])

    planned_duration_days = max((planned_end - planned_start).days, 1)
    days_elapsed          = max((as_of - planned_start).days, 0)

    expected_progress = float(
        np.clip((days_elapsed / planned_duration_days) * 100, 0.0, 100.0)
    )

    # ── 1. Progress gap ──────────────────────────────────────────────────────
    features["progress_gap"] = expected_progress - actual_progress

    # ── 2. Velocity features ─────────────────────────────────────────────────
    df["_days_diff"] = df["update_date"].diff().dt.days.clip(lower=0)
    df["_prog_diff"] = df["physical_progress_pct"].diff().fillna(0.0)

    def _velocity_over_n_updates(n: int) -> float:
        if len(df) < 2:
            return 0.0
        window = df.tail(n + 1) if len(df) > n else df
        prog_gained = window["physical_progress_pct"].iloc[-1] - window["physical_progress_pct"].iloc[0]
        days_passed = (window["update_date"].iloc[-1] - window["update_date"].iloc[0]).days
        return prog_gained / days_passed if days_passed > 0 else 0.0

    features["velocity_last_1"] = _velocity_over_n_updates(1)
    features["velocity_last_3"] = _velocity_over_n_updates(3)
    features["velocity_last_6"] = _velocity_over_n_updates(6)

    remaining_progress  = max(0.0, 100.0 - actual_progress)
    days_to_planned_end = (planned_end - as_of).days

    if days_to_planned_end > 0:
        features["velocity_needed_to_finish"] = remaining_progress / days_to_planned_end
    else:
        features["velocity_needed_to_finish"] = 999.0 if remaining_progress > 0 else 0.0

    # ── 3. Milestone features ─────────────────────────────────────────────────
    m_cols = ["milestone_name", "milestone_planned_date", "milestone_expected_date", "milestone_actual_date"]
    milestones = (
        df[m_cols]
        .dropna(subset=["milestone_name"])
        .copy()
    )

    max_delay_months = 0.0
    delayed_count    = 0

    unique_milestones = milestones.groupby("milestone_name").last()
    total_milestones  = len(unique_milestones)

    if total_milestones == 0:
        flags["milestone_data_missing"] = 1
        features["pct_milestones_delayed"]    = 0.0
        features["max_milestone_delay_months"] = 0.0
    else:
        for _, m in unique_milestones.iterrows():
            m_planned = pd.Timestamp(m["milestone_planned_date"]) if pd.notna(m["milestone_planned_date"]) else None
            if m_planned is None:
                continue
            if pd.notna(m.get("milestone_actual_date")):
                ref = pd.Timestamp(m["milestone_actual_date"])
            elif pd.notna(m.get("milestone_expected_date")):
                ref = pd.Timestamp(m["milestone_expected_date"])
            else:
                continue
            delay_months = (ref - m_planned).days / 30.44
            if delay_months > 0:
                delayed_count += 1
                max_delay_months = max(max_delay_months, delay_months)

        features["pct_milestones_delayed"]    = delayed_count / total_milestones
        features["max_milestone_delay_months"] = max_delay_months

    # ── 4. Cost features ─────────────────────────────────────────────────────
    features["cost_growth_pct"] = (revised_cost - sanctioned_cost) / sanctioned_cost * 100.0

    if actual_progress > 0:
        features["expenditure_to_progress_ratio"] = (
            (cum_expenditure / sanctioned_cost) / (actual_progress / 100.0)
        )
    else:
        features["expenditure_to_progress_ratio"] = 0.0

    # Burn rate: spend per day over last 4 updates
    if len(df) >= 4:
        recent = df.tail(4)
        cost_delta = (
            recent["cumulative_expenditure"].iloc[-1]
            - recent["cumulative_expenditure"].iloc[0]
        )
        days_delta = (recent["update_date"].iloc[-1] - recent["update_date"].iloc[0]).days
        features["burn_rate_per_day"] = cost_delta / days_delta if days_delta > 0 else 0.0
    else:
        features["burn_rate_per_day"] = 0.0

    # ── 5. Update-cadence features ────────────────────────────────────────────
    features["days_since_last_update"] = (as_of - df["update_date"].iloc[-1]).days
    avg_gap = df["_days_diff"].iloc[1:].mean() if len(df) > 1 else 0.0
    features["avg_update_gap"] = 0.0 if np.isnan(avg_gap) else float(avg_gap)

    # Count distinct expected_completion dates (revision counter)
    n_distinct_exp = df["expected_completion_date"].nunique()
    features["count_of_revised_dates"] = max(0, n_distinct_exp - 1)

    # ── 6. Project-level context ──────────────────────────────────────────────
    features["project_age_days"]       = float(days_elapsed)
    features["planned_duration_days"]  = float(planned_duration_days)
    features["n_updates_so_far"]       = float(len(df))

    # ── 7. Categoricals (native strings — callers do OHE if needed) ──────────
    features["sector"]   = str(latest.get("sector",   "Unknown"))
    features["ministry"] = str(latest.get("ministry", "Unknown"))
    features["agency"]   = str(latest.get("agency",   "Unknown"))

    # ── 8. Missingness flags ─────────────────────────────────────────────────
    features.update(flags)

    # ── 9. Final NaN guard ───────────────────────────────────────────────────
    for k, v in features.items():
        if isinstance(v, float) and (np.isnan(v) or np.isinf(v)):
            features[k] = 0.0

    return features


# ── Label computation ──────────────────────────────────────────────────────────

def compute_labels(
    project_df: pd.DataFrame,
    as_of_date: str,
    sector: str = "Default",
) -> Dict[str, int]:
    """
    Compute the three target labels for a project using ONLY outcome columns
    (final_cost, final_end_date) which are constant per project.

    Parameters
    ----------
    project_df : pd.DataFrame  Full project history (any period).
    as_of_date : str           Cutoff — used to compute impl_risk.
    sector : str               For sector-specific cost tolerance.

    Returns
    -------
    dict with keys: label_overrun, label_delay, label_impl_risk
    """
    as_of = pd.Timestamp(as_of_date)
    project_df = project_df.copy()
    project_df["update_date"] = pd.to_datetime(project_df["update_date"])

    last = project_df.iloc[-1]

    sanctioned   = float(last["sanctioned_cost"])
    final_cost   = float(last["final_cost"])
    planned_end  = pd.Timestamp(last["planned_end"])
    planned_start= pd.Timestamp(last["planned_start"])
    final_end    = pd.Timestamp(last["final_end_date"])

    tol_cost = SECTOR_COST_TOLERANCE.get(sector, SECTOR_COST_TOLERANCE["Default"])
    label_overrun = int(final_cost > sanctioned * (1 + tol_cost))

    planned_duration_days = max((planned_end - planned_start).days, 1)
    time_tolerance_days   = max(90, planned_duration_days * 0.10)
    label_delay = int((final_end - planned_end).days > time_tolerance_days)

    # Implementation risk: stagnation in 6-month forward window
    future = project_df[
        (project_df["update_date"] > as_of) &
        (project_df["update_date"] <= as_of + pd.Timedelta(days=182))
    ]
    past_progress = project_df[project_df["update_date"] <= as_of]["physical_progress_pct"]
    current_progress = float(past_progress.iloc[-1]) if not past_progress.empty else 0.0

    label_impl_risk = 0
    if not future.empty:
        max_future_progress = future["physical_progress_pct"].max()
        if max_future_progress - current_progress < 3.0:  # stagnation threshold
            label_impl_risk = 1
    elif label_delay == 1 or label_overrun == 1:
        label_impl_risk = 1

    return {
        "label_overrun":   label_overrun,
        "label_delay":     label_delay,
        "label_impl_risk": label_impl_risk,
    }


# ── Training dataset builder ───────────────────────────────────────────────────

def build_training_dataset(
    df: pd.DataFrame,
    as_of_dates: List[str],
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Build a point-in-time labelled dataset across multiple cutoff dates.

    Parameters
    ----------
    df : pd.DataFrame
        Full raw dataset (from generator or CSV).
    as_of_dates : list[str]
        List of ISO date strings for rolling-origin backtesting.
    verbose : bool
        Print progress info.

    Returns
    -------
    pd.DataFrame
        One row per (project_id, as_of_date) with all features + labels.
    """
    df = df.copy()
    df["update_date"] = pd.to_datetime(df["update_date"])

    records: List[Dict[str, Any]] = []
    errors = 0

    for as_of in as_of_dates:
        as_of_ts = pd.Timestamp(as_of)
        if verbose:
            print(f"  Processing cutoff: {as_of} ...", end=" ", flush=True)

        count = 0
        for pid, grp_full in df.groupby("project_id"):
            # Only projects that had at least one update before/at as_of
            grp_past = grp_full[grp_full["update_date"] <= as_of_ts].copy()
            if grp_past.empty:
                continue

            sector = str(grp_full.iloc[-1].get("sector", "Default"))

            try:
                feats = compute_features(grp_past, as_of)
                if feats is None:
                    continue
                labels = compute_labels(grp_full, as_of, sector)
            except ValueError as exc:
                errors += 1
                if verbose and errors <= 5:
                    print(f"\n    [WARN] {pid}: {exc}")
                continue

            rec = {"project_id": pid, "as_of_date": as_of}
            rec.update(feats)
            rec.update(labels)
            records.append(rec)
            count += 1

        if verbose:
            print(f"{count} records.")

    if verbose:
        print(f"Total: {len(records):,} records built. Leakage errors skipped: {errors}")

    return pd.DataFrame(records)


# ── Temporal train/val/test split ─────────────────────────────────────────────

def temporal_split(
    features_df: pd.DataFrame,
    train_cutoffs: List[str],
    val_cutoffs: List[str],
    test_cutoffs: List[str],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Split features_df into train/val/test based on the as_of_date column.
    No project leaks across splits for the same horizon.
    """
    train = features_df[features_df["as_of_date"].isin(train_cutoffs)].copy()
    val   = features_df[features_df["as_of_date"].isin(val_cutoffs)].copy()
    test  = features_df[features_df["as_of_date"].isin(test_cutoffs)].copy()
    return train, val, test
