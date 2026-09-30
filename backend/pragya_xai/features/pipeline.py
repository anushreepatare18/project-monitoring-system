"""
PRAGYA XAI — /features/pipeline.py
Shared feature computation used identically for training AND inference.
Automated leakage guard: raises ValueError if any data row is after as_of_date.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from typing import Any, Dict, List, Optional

# ── Column groups (exported for training/inference use) ────────────────────────
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
]

# Sector-level cost overrun tolerance (%)
SECTOR_TOLERANCE: Dict[str, float] = {
    "Highways": 0.15,
    "Railways": 0.12,
    "Power Generation": 0.10,
    "Default": 0.10,
}


def compute_features(
    project_df: pd.DataFrame,
    as_of_date: str,
) -> Optional[Dict[str, Any]]:
    """
    Compute risk-prediction features for ONE project as of *as_of_date*.

    Parameters
    ----------
    project_df : DataFrame of all update rows for a single project.
                 The caller is responsible for NOT passing future rows
                 (the leakage guard will raise if any slip through).
    as_of_date : 'YYYY-MM-DD' string.

    Returns None if there is no data before as_of_date.
    Raises ValueError on leakage.
    """
    as_of = pd.Timestamp(as_of_date)

    df = project_df.copy()
    df["update_date"] = pd.to_datetime(df["update_date"])

    # ── AUTOMATED LEAKAGE CHECK ───────────────────────────────────────────────
    future_mask = df["update_date"] > as_of
    if future_mask.any():
        bad = df.loc[future_mask, "update_date"].dt.date.tolist()
        raise ValueError(
            f"[LEAKAGE] {future_mask.sum()} row(s) after as_of_date={as_of_date}: "
            f"{bad[:5]} ..."
        )

    df = df[df["update_date"] <= as_of].sort_values("update_date").reset_index(drop=True)
    if df.empty:
        return None

    latest = df.iloc[-1]
    feats: Dict[str, Any] = {}
    flags: Dict[str, int] = {f: 0 for f in MISSINGNESS_FLAGS}

    def _get(col: str, default: float = 0.0) -> float:
        v = latest.get(col)
        if v is None or (isinstance(v, float) and np.isnan(v)):
            flags.get(f"{col}_missing") and None  # silently skip unknown flags
            if f"{col}_missing" in flags:
                flags[f"{col}_missing"] = 1
            return default
        try:
            return float(v)
        except (TypeError, ValueError):
            return default

    # Raw values
    actual_prog  = _get("physical_progress_pct", 0.0)
    sanc_cost    = max(_get("sanctioned_cost", 1.0), 1.0)
    cum_exp      = _get("cumulative_expenditure", 0.0)
    rev_cost     = _get("revised_cost", sanc_cost)

    planned_start = pd.Timestamp(latest["planned_start"])
    planned_end   = pd.Timestamp(latest["planned_end"])
    planned_dur   = max((planned_end - planned_start).days, 1)
    elapsed       = max((as_of - planned_start).days, 0)
    exp_prog      = float(np.clip(elapsed / planned_dur * 100, 0, 100))

    # ── 1. Progress gap ───────────────────────────────────────────────────────
    feats["progress_gap"] = exp_prog - actual_prog

    # ── 2. Velocity features ──────────────────────────────────────────────────
    df["_days"] = df["update_date"].diff().dt.days.clip(lower=0)
    df["_prog"] = df["physical_progress_pct"].diff().fillna(0)

    def _vel(n: int) -> float:
        if len(df) < 2:
            return 0.0
        win   = df.tail(n + 1) if len(df) > n else df
        prog  = win["physical_progress_pct"].iloc[-1] - win["physical_progress_pct"].iloc[0]
        days  = (win["update_date"].iloc[-1] - win["update_date"].iloc[0]).days
        return prog / days if days > 0 else 0.0

    feats["velocity_last_1"] = _vel(1)
    feats["velocity_last_3"] = _vel(3)
    feats["velocity_last_6"] = _vel(6)

    remain     = max(0.0, 100.0 - actual_prog)
    days_left  = (planned_end - as_of).days
    feats["velocity_needed_to_finish"] = (
        remain / days_left if days_left > 0 else (999.0 if remain > 0 else 0.0)
    )

    # ── 3. Milestone features ─────────────────────────────────────────────────
    m_cols = ["milestone_name", "milestone_planned_date",
              "milestone_expected_date", "milestone_actual_date"]
    ms = df[m_cols].dropna(subset=["milestone_name"]).copy()
    if ms.empty:
        flags["milestone_data_missing"] = 1
        feats["pct_milestones_delayed"]    = 0.0
        feats["max_milestone_delay_months"] = 0.0
    else:
        delayed = 0
        max_del = 0.0
        for _, row in ms.groupby("milestone_name").last().iterrows():
            m_plan = pd.Timestamp(row["milestone_planned_date"]) if pd.notna(row["milestone_planned_date"]) else None
            if m_plan is None:
                continue
            ref = (pd.Timestamp(row["milestone_actual_date"])
                   if pd.notna(row.get("milestone_actual_date"))
                   else (pd.Timestamp(row["milestone_expected_date"])
                         if pd.notna(row.get("milestone_expected_date")) else None))
            if ref is None:
                continue
            delay_mo = (ref - m_plan).days / 30.44
            if delay_mo > 0:
                delayed += 1
                max_del  = max(max_del, delay_mo)
        total = len(ms["milestone_name"].unique())
        feats["pct_milestones_delayed"]    = delayed / total if total else 0.0
        feats["max_milestone_delay_months"] = max_del

    # ── 4. Cost features ──────────────────────────────────────────────────────
    feats["cost_growth_pct"]              = (rev_cost - sanc_cost) / sanc_cost * 100
    feats["expenditure_to_progress_ratio"] = (
        (cum_exp / sanc_cost) / (actual_prog / 100) if actual_prog > 0 else 0.0
    )
    if len(df) >= 4:
        w = df.tail(4)
        cost_d = w["cumulative_expenditure"].iloc[-1] - w["cumulative_expenditure"].iloc[0]
        day_d  = (w["update_date"].iloc[-1] - w["update_date"].iloc[0]).days
        feats["burn_rate_per_day"] = cost_d / day_d if day_d > 0 else 0.0
    else:
        feats["burn_rate_per_day"] = 0.0

    # ── 5. Update-cadence features ────────────────────────────────────────────
    feats["days_since_last_update"] = (as_of - df["update_date"].iloc[-1]).days
    avg_gap = df["_days"].iloc[1:].mean() if len(df) > 1 else 0.0
    feats["avg_update_gap"]         = 0.0 if (isinstance(avg_gap, float) and np.isnan(avg_gap)) else float(avg_gap)
    n_distinct = df["expected_completion_date"].nunique() if "expected_completion_date" in df.columns else 1
    feats["count_of_revised_dates"] = max(0, n_distinct - 1)

    # ── 6. Project-level context ──────────────────────────────────────────────
    feats["project_age_days"]      = float(elapsed)
    feats["planned_duration_days"] = float(planned_dur)
    feats["n_updates_so_far"]      = float(len(df))

    # ── 7. Categoricals ───────────────────────────────────────────────────────
    feats["sector"]   = str(latest.get("sector",   "Unknown"))
    feats["ministry"] = str(latest.get("ministry", "Unknown"))
    feats["agency"]   = str(latest.get("agency",   "Unknown"))

    feats.update(flags)

    # ── 8. Final NaN guard ────────────────────────────────────────────────────
    for k, v in feats.items():
        if isinstance(v, float) and (np.isnan(v) or np.isinf(v)):
            feats[k] = 0.0

    return feats


def compute_labels(
    project_df: pd.DataFrame,
    sector: str = "Default",
    delay_tolerance_days: int = 90,
) -> Dict[str, int]:
    """
    Compute binary labels for one project using ONLY outcome columns.
    These are constant per project regardless of as_of_date.
    """
    last = project_df.iloc[-1]
    sanc      = float(last["sanctioned_cost"])
    final_cost= float(last["final_cost"])
    p_start   = pd.Timestamp(last["planned_start"])
    p_end     = pd.Timestamp(last["planned_end"])
    f_end     = pd.Timestamp(last["final_end_date"])

    tol_cost = SECTOR_TOLERANCE.get(sector, SECTOR_TOLERANCE["Default"])
    label_overrun = int(final_cost > sanc * (1 + tol_cost))

    duration_tol = max(delay_tolerance_days, int((p_end - p_start).days * 0.10))
    label_delay  = int((f_end - p_end).days > duration_tol)

    return {"label_overrun": label_overrun, "label_delay": label_delay}


def build_training_dataset(
    df: pd.DataFrame,
    as_of_dates: List[str],
    verbose: bool = True,
) -> pd.DataFrame:
    """Build a labelled, point-in-time feature dataset across multiple cutoffs."""
    df = df.copy()
    df["update_date"] = pd.to_datetime(df["update_date"])
    records = []
    skipped = 0

    for as_of in as_of_dates:
        ts = pd.Timestamp(as_of)
        n  = 0
        for pid, grp_full in df.groupby("project_id"):
            grp_past = grp_full[grp_full["update_date"] <= ts].copy()
            if grp_past.empty:
                continue
            sector = str(grp_full.iloc[-1].get("sector", "Default"))
            try:
                feats  = compute_features(grp_past, as_of)
                labels = compute_labels(grp_full, sector)
            except ValueError:
                skipped += 1
                continue
            if feats is None:
                continue
            rec = {"project_id": pid, "as_of_date": as_of, **feats, **labels}
            records.append(rec)
            n += 1
        if verbose:
            print(f"  Cutoff {as_of}: {n} records")

    if verbose:
        print(f"  Total: {len(records)}, skipped (leakage): {skipped}")
    return pd.DataFrame(records)
