"""
PRAGYA AI — Synthetic Data Generator  (v2)
Generates ~2,000 projects × 5–12 periodic updates with:
  - Realistic noise + anomaly injections (~10% of projects)
  - Genuine mix of on-time / delayed / overrun / implementation-risk projects
  - All fields required by the feature pipeline and label builder
  - Fixed random seed for full reproducibility
"""
from __future__ import annotations

import datetime
import os
import random
from pathlib import Path
from typing import List, Optional

import numpy as np
import pandas as pd

# ── Constants ────────────────────────────────────────────────────────────────
SECTORS = [
    "Roads", "Railways", "Power", "Health", "Education",
    "Water", "Irrigation", "Telecom", "Ports", "Airports",
    "Smart_Cities", "Urban_Dev", "Defence", "Agriculture",
    "Housing", "Forestry", "Mining", "Textiles", "Pharma", "IT",
]
MINISTRIES = [
    "MoRTH", "MoR", "MoPNG", "MoH", "MoE",
    "MoJal", "MoA", "MoComm", "MoSP", "MoAEF",
]
AGENCIES  = [f"Agency_{i}" for i in range(1, 51)]
STATES    = [
    "MH", "KA", "DL", "UP", "TN", "GJ", "WB", "RJ", "MP", "AP",
    "OD", "TS", "KL", "HR", "PB", "BR", "JH", "CG", "AS", "HP",
]
PROJECT_TYPES = ["Construction", "Renovation", "IT_Rollout", "Procurement", "Research"]

# Sector-level cost-overrun tolerance (fraction above sanctioned cost)
SECTOR_TOLERANCE: dict[str, float] = {s: 0.10 for s in SECTORS}
SECTOR_TOLERANCE["Roads"]    = 0.12
SECTOR_TOLERANCE["Railways"] = 0.15

# Milestone names used within each project
MILESTONE_NAMES = [
    "Land Acquisition",
    "Foundation / Design Approval",
    "50% Physical Completion",
    "Civil Works Completion",
    "Commissioning / Handover",
]


def generate_synthetic_data(
    num_projects: int = 2000,
    output_file: str = "ml_core/data/synthetic_projects.csv",
    random_seed: int = 42,
) -> pd.DataFrame:
    """
    Generate the synthetic project-update dataset.
    Returns the full DataFrame and saves it to *output_file*.

    Schema (one row = one periodic update):
      Identifiers/context: project_id, ministry, sector, agency, state,
          sanctioned_cost, planned_start, planned_end, project_type
      Progress fields: physical_progress_pct, financial_progress_pct,
          cumulative_expenditure, revised_cost, expected_completion_date
      Milestone (active at this update): milestone_name,
          milestone_planned_date, milestone_expected_date, milestone_actual_date
      Outcome (label extraction only, NEVER used as features):
          final_cost, final_end_date, delayed_flag, overrun_flag,
          implementation_risk_flag, outcome_known_at
      Anomaly marker: is_anomaly_injection
    """
    np.random.seed(random_seed)
    random.seed(random_seed)

    records: List[dict] = []
    used_ids: set[str] = set()

    for _ in range(num_projects):
        # ── Project identity ─────────────────────────────────────────────────
        while True:
            pid = f"PRJ-{np.random.randint(100000, 999999):06d}"
            if pid not in used_ids:
                used_ids.add(pid)
                break

        sector    = random.choice(SECTORS)
        ministry  = random.choice(MINISTRIES)
        agency    = f"Agency_{random.randint(1, 50)}"
        state     = random.choice(STATES)
        p_type    = random.choice(PROJECT_TYPES)

        sanctioned_cost = round(np.random.lognormal(mean=4.5, sigma=1.5), 2)

        # ── Timeline ─────────────────────────────────────────────────────────
        start_date   = datetime.date(2018, 1, 1) + datetime.timedelta(
            days=random.randint(0, 1825)
        )
        duration_days = random.randint(300, 1800)
        planned_end   = start_date + datetime.timedelta(days=duration_days)

        # ── Outcome / label flags ─────────────────────────────────────────────
        tol        = SECTOR_TOLERANCE[sector]
        is_delayed = np.random.rand() < 0.30
        is_overrun = np.random.rand() < 0.25
        # Correlated: 40 % of delayed projects also overrun
        if is_delayed and np.random.rand() < 0.40:
            is_overrun = True

        delay_factor   = random.uniform(1.10, 1.60) if is_delayed else random.uniform(0.92, 1.05)
        actual_duration = max(1, int(duration_days * delay_factor))
        final_end_date  = start_date + datetime.timedelta(days=actual_duration)

        overrun_factor = (
            random.uniform(1 + tol + 0.01, 1.50) if is_overrun
            else random.uniform(0.95, 1 + tol - 0.01)
        )
        final_cost = round(sanctioned_cost * overrun_factor, 2)

        # implementation_risk: stagnation / high delay ratio within 6-month fwd window
        is_impl_risk = is_delayed and (delay_factor > 1.25) or (np.random.rand() < 0.08)

        outcome_known_at = final_end_date + datetime.timedelta(days=random.randint(30, 90))

        # ── Milestones (up to 5 per project) ─────────────────────────────────
        n_milestones = random.randint(3, 5)
        milestones: List[dict] = []
        for m_idx in range(n_milestones):
            frac      = (m_idx + 1) / (n_milestones + 1)
            m_planned = start_date + datetime.timedelta(days=int(duration_days * frac))
            m_delay_d = random.randint(0, 150) if is_delayed else 0
            m_expected = m_planned + datetime.timedelta(days=m_delay_d)
            milestones.append({
                "name":     MILESTONE_NAMES[m_idx % len(MILESTONE_NAMES)],
                "planned":  m_planned,
                "expected": m_expected,
            })

        # ── Updates ──────────────────────────────────────────────────────────
        num_updates      = random.randint(5, 12)
        update_interval  = actual_duration / num_updates
        anomaly_idx      = (
            random.randint(1, num_updates - 2) if np.random.rand() < 0.10 else -1
        )

        for u in range(num_updates):
            update_date = start_date + datetime.timedelta(
                days=int((u + 1) * update_interval)
            )
            update_date = min(update_date, final_end_date)

            progress_ratio  = min(1.0, (update_date - start_date).days / max(1, actual_duration))
            physical_prog   = min(100.0, progress_ratio * 100 * np.random.uniform(0.80, 1.15))
            financial_prog  = min(100.0, progress_ratio * 100 * np.random.uniform(0.80, 1.15))
            cum_expenditure = round((financial_prog / 100.0) * final_cost, 2)

            # Anomaly injection: expenditure spike + physical drop
            if u == anomaly_idx:
                cum_expenditure = round(cum_expenditure * np.random.uniform(2.2, 3.5), 2)
                physical_prog   = max(0.0, physical_prog - random.uniform(15, 30))

            # Revised cost: grows for overrun projects after midpoint
            revised_cost = sanctioned_cost
            if is_overrun and u > num_updates // 2:
                revised_cost = round(final_cost * random.uniform(0.88, 1.00), 2)

            # Expected-completion drift for delayed projects
            expected_completion = planned_end
            if is_delayed and u > num_updates // 3:
                drift_days = random.randint(30, 180)
                expected_completion = final_end_date - datetime.timedelta(
                    days=max(0, drift_days - u * 10)
                )

            # Active milestone at this update
            m_bucket = min(u // max(1, num_updates // n_milestones), n_milestones - 1)
            active_m = milestones[m_bucket]
            m_actual_date: Optional[str] = None
            if update_date >= active_m["planned"]:
                m_actual_dt = active_m["expected"] + datetime.timedelta(
                    days=random.randint(-5, 30)
                )
                m_actual_date = m_actual_dt.strftime("%Y-%m-%d")

            count_revised = 1 if expected_completion > planned_end else 0

            records.append({
                # --- Identifiers / context ---
                "project_id":               pid,
                "update_date":              update_date.strftime("%Y-%m-%d"),
                "ministry":                 ministry,
                "sector":                   sector,
                "agency":                   agency,
                "state":                    state,
                "sanctioned_cost":          sanctioned_cost,
                "planned_start":            start_date.strftime("%Y-%m-%d"),
                "planned_end":              planned_end.strftime("%Y-%m-%d"),
                "project_type":             p_type,
                # --- Progress ---
                "physical_progress_pct":    round(physical_prog, 2),
                "financial_progress_pct":   round(financial_prog, 2),
                "cumulative_expenditure":   round(cum_expenditure, 2),
                "revised_cost":             round(revised_cost, 2),
                "expected_completion_date": expected_completion.strftime("%Y-%m-%d"),
                # --- Active milestone ---
                "milestone_name":           active_m["name"],
                "milestone_planned_date":   active_m["planned"].strftime("%Y-%m-%d"),
                "milestone_expected_date":  active_m["expected"].strftime("%Y-%m-%d"),
                "milestone_actual_date":    m_actual_date if m_actual_date else "",
                # --- Outcome labels (MUST NOT be used as features) ---
                "final_cost":               final_cost,
                "final_end_date":           final_end_date.strftime("%Y-%m-%d"),
                "delayed_flag":             int(is_delayed),
                "overrun_flag":             int(is_overrun),
                "implementation_risk_flag": int(bool(is_impl_risk)),
                "outcome_known_at":         outcome_known_at.strftime("%Y-%m-%d"),
                # --- Anomaly marker (for reference / anomaly model training) ---
                "is_anomaly_injection":     int(u == anomaly_idx),
            })

    df = pd.DataFrame(records)
    df["update_date"] = pd.to_datetime(df["update_date"])
    df = df.sort_values(["update_date", "project_id"]).reset_index(drop=True)

    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_file, index=False)
    print(
        f"[generator] Generated {len(df):,} updates across "
        f"{num_projects:,} projects -> {output_file}"
    )
    return df


if __name__ == "__main__":
    generate_synthetic_data(output_file="ml_core/data/synthetic_projects.csv")
