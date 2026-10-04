"""
PRAGYA AI — Results Store  (mock)
===================================
A queryable, in-memory (Pandas) results store that holds pre-computed
risk scores, SHAP top-reasons, anomaly flags, and benchmark percentiles
for every project × as-of-date snapshot.

In production this would be a materialized SQL view updated nightly.
For standalone testing / chatbot use, this module provides:
  - A deterministic mock store (seeded from synthetic data if available)
  - A clean interface matching the real schema:
      project_id, as_of_date, sector, ministry, agency, state,
      sanctioned_cost, planned_start, planned_end, project_type,
      physical_progress_pct, cumulative_expenditure,
      expected_completion_date,
      p_cost, p_time, p_impl, composite_risk_score, risk_band,
      top_reasons (list[str]), anomaly_score, anomaly_flag,
      milestone_delay_months, cost_growth_pct,
      sector_percentile_risk
"""
from __future__ import annotations

import json
import os
import random
from datetime import date, timedelta
from typing import Optional

import numpy as np
import pandas as pd

# ── Known valid domain values ─────────────────────────────────────────────────
VALID_SECTORS = [
    "Roads", "Railways", "Power", "Health", "Education",
    "Water", "Irrigation", "Telecom", "Ports", "Airports",
    "Smart_Cities", "Urban_Dev", "Defence", "Agriculture",
    "Housing", "Forestry", "Mining", "Textiles", "Pharma", "IT",
]
VALID_MINISTRIES = [
    "MoRTH", "MoR", "MoPNG", "MoH", "MoE",
    "MoJal", "MoA", "MoComm", "MoSP", "MoAEF",
]
VALID_RISK_BANDS = ["Low", "Medium", "High", "Critical"]

_STORE: Optional[pd.DataFrame] = None   # module-level singleton


def _build_mock_store(n: int = 200, seed: int = 42) -> pd.DataFrame:
    """
    Build a deterministic mock results store.
    If synthetic_projects.csv exists, samples from it for realism.
    Otherwise generates purely synthetic rows.
    """
    rng = np.random.default_rng(seed)
    random.seed(seed)

    # Try to read real synthetic data
    real_path = "ml_core/data/synthetic_projects.csv"
    base_df: Optional[pd.DataFrame] = None
    if os.path.exists(real_path):
        try:
            raw = pd.read_csv(real_path)
            raw["update_date"] = pd.to_datetime(raw["update_date"])
            # Take the latest update per project
            base_df = (
                raw.sort_values("update_date")
                   .groupby("project_id")
                   .tail(1)
                   .reset_index(drop=True)
                   .sample(min(n, len(raw["project_id"].unique())), random_state=seed)
            )
        except Exception:
            base_df = None

    records = []
    n_actual = len(base_df) if base_df is not None else n

    for i in range(n_actual):
        if base_df is not None:
            row = base_df.iloc[i]
            pid      = str(row["project_id"])
            sector   = str(row["sector"])
            ministry = str(row["ministry"])
            agency   = str(row["agency"])
            state    = str(row.get("state", "MH"))
            p_type   = str(row.get("project_type", "Construction"))
            sc       = float(row["sanctioned_cost"])
            ps       = str(row["planned_start"])
            pe       = str(row["planned_end"])
            phys     = float(row["physical_progress_pct"])
            cum_exp  = float(row["cumulative_expenditure"])
            ecd      = str(row["expected_completion_date"])
            as_of    = str(row["update_date"].date())
            m_delay  = float(rng.uniform(0, 8) if rng.random() < 0.3 else 0.0)
            c_growth = float(rng.uniform(-2, 40) if rng.random() < 0.25 else rng.uniform(-2, 10))
        else:
            pid      = f"PRJ-{100000 + i:06d}"
            sector   = random.choice(VALID_SECTORS)
            ministry = random.choice(VALID_MINISTRIES)
            agency   = f"Agency_{rng.integers(1, 51)}"
            state    = random.choice(["MH", "KA", "DL", "UP", "TN", "GJ"])
            p_type   = random.choice(["Construction", "Renovation", "IT_Rollout"])
            sc       = round(float(rng.lognormal(4.5, 1.5)), 2)
            start_d  = date(2019, 1, 1) + timedelta(days=int(rng.integers(0, 1500)))
            dur_d    = int(rng.integers(300, 1800))
            ps       = str(start_d)
            pe       = str(start_d + timedelta(days=dur_d))
            elapsed  = int(rng.integers(60, dur_d))
            as_of    = str(start_d + timedelta(days=elapsed))
            phys     = float(rng.uniform(5, 95))
            cum_exp  = round(phys / 100 * sc * float(rng.uniform(0.8, 1.3)), 2)
            ecd      = pe
            m_delay  = float(rng.uniform(0, 8) if rng.random() < 0.3 else 0.0)
            c_growth = float(rng.uniform(-2, 40) if rng.random() < 0.25 else rng.uniform(-2, 10))

        # Simulate model outputs
        p_cost = float(np.clip(rng.beta(2, 5) + (0.3 if c_growth > 15 else 0), 0, 1))
        p_time = float(np.clip(rng.beta(2, 5) + (0.25 if m_delay > 3 else 0), 0, 1))
        p_impl = float(np.clip(rng.beta(1.5, 6), 0, 1))
        composite = p_cost * 0.4 + p_time * 0.4 + p_impl * 0.2

        if composite > 0.70:
            risk_band = "Critical"
        elif composite > 0.40:
            risk_band = "High"
        elif composite > 0.20:
            risk_band = "Medium"
        else:
            risk_band = "Low"

        anomaly_score = float(rng.uniform(-0.3, 0.3))
        anomaly_flag  = bool(anomaly_score < -0.15)

        top_reasons = _mock_reasons(p_cost, p_time, m_delay, c_growth, phys)

        records.append({
            "project_id":               pid,
            "as_of_date":               as_of,
            "sector":                   sector,
            "ministry":                 ministry,
            "agency":                   agency,
            "state":                    state,
            "project_type":             p_type,
            "sanctioned_cost":          sc,
            "planned_start":            ps,
            "planned_end":              pe,
            "physical_progress_pct":    round(phys, 1),
            "cumulative_expenditure":   cum_exp,
            "expected_completion_date": ecd,
            "p_cost":                   round(p_cost, 4),
            "p_time":                   round(p_time, 4),
            "p_impl":                   round(p_impl, 4),
            "composite_risk_score":     round(composite, 4),
            "risk_band":                risk_band,
            "top_reasons":              json.dumps(top_reasons),
            "anomaly_score":            round(anomaly_score, 4),
            "anomaly_flag":             anomaly_flag,
            "milestone_delay_months":   round(m_delay, 1),
            "cost_growth_pct":          round(c_growth, 1),
        })

    df = pd.DataFrame(records)

    # Add sector_percentile_risk (rank within sector)
    df["sector_percentile_risk"] = (
        df.groupby("sector")["composite_risk_score"]
          .rank(pct=True)
          .round(2)
    )
    return df


def _mock_reasons(
    p_cost: float, p_time: float, m_delay: float, c_growth: float, phys: float
) -> list[str]:
    reasons: list[str] = []
    if phys < 40:
        reasons.append(f"Progress is {100-phys:.1f}% below the expected level at this stage, which increases risk.")
    if m_delay > 1:
        reasons.append(f"A key milestone is delayed by {m_delay:.1f} months, which increases risk.")
    if c_growth > 10:
        reasons.append(f"Revised cost has grown {c_growth:.1f}% above the sanctioned budget, which increases risk.")
    if p_time > 0.5:
        reasons.append("Completion velocity is insufficient to meet the planned deadline, which increases risk.")
    if not reasons:
        reasons.append("Project is progressing within expected parameters.")
    return reasons


# ── Public interface ──────────────────────────────────────────────────────────

def get_store() -> pd.DataFrame:
    """Return the singleton results store (building it on first call)."""
    global _STORE
    if _STORE is None:
        _STORE = _build_mock_store()
    return _STORE


def query_store(
    sector: Optional[str]    = None,
    ministry: Optional[str]  = None,
    agency: Optional[str]    = None,
    risk_band: Optional[str] = None,
    min_risk_score: Optional[float]          = None,
    max_risk_score: Optional[float]          = None,
    min_milestone_delay_months: Optional[float] = None,
    project_ids: Optional[list[str]]         = None,
    anomaly_flag: Optional[bool]             = None,
    sort_by: str  = "composite_risk_score",
    sort_asc: bool = False,
    limit: int    = 20,
    scope_ministry: Optional[str]            = None,   # RBAC filter
) -> pd.DataFrame:
    """
    Execute a structured query against the results store.
    All filters are additive (AND-logic).
    `scope_ministry` is the RBAC boundary: None or "ALL" means no restriction.

    Returns a filtered, sorted, limited DataFrame.
    """
    df = get_store().copy()

    # RBAC scope filter (always applied first)
    if scope_ministry and scope_ministry.upper() != "ALL":
        df = df[df["ministry"] == scope_ministry]

    if sector:
        df = df[df["sector"].str.lower() == sector.lower()]
    if ministry:
        df = df[df["ministry"].str.lower() == ministry.lower()]
    if agency:
        df = df[df["agency"].str.lower() == agency.lower()]
    if risk_band:
        df = df[df["risk_band"].str.lower() == risk_band.lower()]
    if min_risk_score is not None:
        df = df[df["composite_risk_score"] >= min_risk_score]
    if max_risk_score is not None:
        df = df[df["composite_risk_score"] <= max_risk_score]
    if min_milestone_delay_months is not None:
        df = df[df["milestone_delay_months"] >= min_milestone_delay_months]
    if project_ids:
        df = df[df["project_id"].isin(project_ids)]
    if anomaly_flag is not None:
        df = df[df["anomaly_flag"] == anomaly_flag]

    if sort_by in df.columns:
        df = df.sort_values(sort_by, ascending=sort_asc)

    return df.head(limit).reset_index(drop=True)


def get_project_record(project_id: str, scope_ministry: Optional[str] = None) -> Optional[dict]:
    """Fetch a single project's latest risk record."""
    df = get_store()
    if scope_ministry and scope_ministry.upper() != "ALL":
        df = df[df["ministry"] == scope_ministry]
    row = df[df["project_id"] == project_id]
    if row.empty:
        return None
    r = row.iloc[0].to_dict()
    # Deserialise top_reasons
    try:
        r["top_reasons"] = json.loads(r["top_reasons"])
    except Exception:
        r["top_reasons"] = []
    return r


def aggregate_by_sector(metric: str = "overrun") -> list[dict]:
    """
    Aggregate the results store by sector.
    metric: 'overrun' | 'delay' | 'anomaly' | 'avg_risk'
    """
    df = get_store()
    if metric == "overrun":
        grouped = (
            df[df["cost_growth_pct"] > 10]
              .groupby("sector")
              .size()
              .reset_index(name="count")
              .sort_values("count", ascending=False)
        )
    elif metric == "delay":
        grouped = (
            df[df["milestone_delay_months"] > 0]
              .groupby("sector")
              .size()
              .reset_index(name="count")
              .sort_values("count", ascending=False)
        )
    elif metric == "anomaly":
        grouped = (
            df[df["anomaly_flag"]]
              .groupby("sector")
              .size()
              .reset_index(name="count")
              .sort_values("count", ascending=False)
        )
    else:   # avg_risk
        grouped = (
            df.groupby("sector")["composite_risk_score"]
              .mean()
              .reset_index(name="avg_risk")
              .sort_values("avg_risk", ascending=False)
        )
    return grouped.to_dict(orient="records")
