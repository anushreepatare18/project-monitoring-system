"""
PRAGYA AI — Synthetic Dataset Generator
Generates ~2,000 government infrastructure projects with realistic
temporal project-update records, labels, anomalies, and milestone data.

Usage:
    python -m backend.ml_core.data.generator
    python backend/ml_core/data/generator.py
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any

import numpy as np
import pandas as pd

# ── Pin seeds for reproducibility ─────────────────────────────────────────────
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

# ── Domain constants ───────────────────────────────────────────────────────────
MINISTRIES: List[str] = [
    "Ministry of Road Transport & Highways",
    "Ministry of Railways",
    "Ministry of Power",
    "Ministry of Petroleum & Natural Gas",
    "Ministry of Water Resources",
    "Ministry of Urban Development",
    "Ministry of Coal",
    "Ministry of Civil Aviation",
    "Ministry of Ports & Shipping",
    "Ministry of Telecom",
]

SECTORS: List[str] = [
    "Highways", "Railways", "Power Generation", "Transmission",
    "Oil & Gas Pipelines", "Urban Metro", "Water Supply",
    "Irrigation", "Ports", "Telecom Infrastructure",
    "Renewable Energy", "Coal Mining", "Steel", "Fertilizers",
    "Petrochemicals", "Airport", "Bridge", "Dam", "Industrial Corridor",
    "Smart Cities",
]

STATES: List[str] = [
    "Maharashtra", "Uttar Pradesh", "Madhya Pradesh", "Gujarat",
    "Rajasthan", "Karnataka", "Tamil Nadu", "Andhra Pradesh",
    "West Bengal", "Odisha", "Jharkhand", "Chhattisgarh",
    "Bihar", "Punjab", "Haryana", "Delhi",
]

PROJECT_TYPES: List[str] = [
    "Greenfield", "Brownfield", "Expansion", "Renovation", "PPP",
]

# Sector-level overrun tolerance (%) for label computation
SECTOR_COST_TOLERANCE: Dict[str, float] = {
    "Highways": 0.15,
    "Railways": 0.12,
    "Power Generation": 0.10,
    "Default": 0.10,
}

AGENCIES: List[str] = [f"Agency_{i:02d}" for i in range(1, 51)]


def _sector_tolerance(sector: str) -> float:
    return SECTOR_COST_TOLERANCE.get(sector, SECTOR_COST_TOLERANCE["Default"])


def generate_synthetic_data(
    num_projects: int = 2000,
    random_seed: int = RANDOM_SEED,
) -> pd.DataFrame:
    """
    Generate a synthetic project-update dataset.

    Returns
    -------
    pd.DataFrame
        One row per (project_id, update_date).
        Columns:
            project_id, update_date, ministry, sector, agency, state,
            sanctioned_cost, planned_start, planned_end, project_type,
            physical_progress_pct, financial_progress_pct,
            cumulative_expenditure, revised_cost, expected_completion_date,
            milestone_name, milestone_planned_date, milestone_expected_date,
            milestone_actual_date,
            final_cost, final_end_date,
            delayed_flag, overrun_flag, outcome_known_at
    """
    rng = np.random.default_rng(random_seed)
    records: List[Dict[str, Any]] = []

    sector_arr = rng.choice(SECTORS, size=num_projects)
    ministry_arr = rng.choice(MINISTRIES, size=num_projects)
    agency_arr = rng.choice(AGENCIES, size=num_projects)
    state_arr = rng.choice(STATES, size=num_projects)
    ptype_arr = rng.choice(PROJECT_TYPES, size=num_projects)

    # Project-level sanctioned cost (log-normal, typical infra in crores INR)
    cost_arr = np.round(rng.lognormal(mean=5.5, sigma=1.2, size=num_projects), 2)

    # Start dates: 2016–2022 spread
    base_date = datetime(2016, 1, 1)
    start_offsets = rng.integers(0, 365 * 6, size=num_projects)

    # Planned durations: 1–6 years
    durations_days = rng.integers(365, 365 * 6, size=num_projects)

    # Outcome flags (pre-determined project fate)
    is_delayed_arr = rng.random(num_projects) < 0.35
    is_overrun_arr = rng.random(num_projects) < 0.28
    # Correlated: many overruns also cause delays
    is_delayed_arr |= (is_overrun_arr & (rng.random(num_projects) < 0.6))

    for i in range(num_projects):
        project_id = f"PRJ-{uuid.uuid4().hex[:8].upper()}"
        ministry   = ministry_arr[i]
        sector     = sector_arr[i]
        agency     = agency_arr[i]
        state      = state_arr[i]
        ptype      = ptype_arr[i]
        sanctioned = float(cost_arr[i])

        planned_start = base_date + timedelta(days=int(start_offsets[i]))
        planned_end   = planned_start + timedelta(days=int(durations_days[i]))

        is_delayed  = bool(is_delayed_arr[i])
        is_overrun  = bool(is_overrun_arr[i])

        # Outcome values
        if is_overrun:
            tol = _sector_tolerance(sector)
            overrun_factor = rng.uniform(1.0 + tol + 0.01, 2.5)
            final_cost = round(sanctioned * overrun_factor, 2)
        else:
            final_cost = round(sanctioned * rng.uniform(0.88, 1.0 + _sector_tolerance(sector) - 0.01), 2)

        if is_delayed:
            delay_days = int(rng.integers(95, 730))
            final_end  = planned_end + timedelta(days=delay_days)
        else:
            early_days = int(rng.integers(0, 90))
            final_end  = planned_end - timedelta(days=early_days)

        outcome_known_at = final_end

        # Number of updates
        n_updates = int(rng.integers(5, 13))
        total_days = (final_end - planned_start).days
        update_offsets = sorted(rng.choice(range(30, total_days), size=n_updates, replace=False))
        update_dates   = [planned_start + timedelta(days=int(d)) for d in update_offsets]

        # ── Per-update simulation ─────────────────────────────────────────
        cum_exp     = 0.0
        phys_prog   = 0.0
        revised_cost = sanctioned
        expected_completion = planned_end
        prev_revised_count  = 0

        milestone_names = [f"M{k}" for k in range(n_updates)]

        for j, upd_date in enumerate(update_dates):
            frac   = (j + 1) / n_updates
            noise  = rng.normal(0, 0.04)

            # ── Anomalous update (2 % of updates) ────────────────────────
            is_anomalous_update = rng.random() < 0.02

            if is_anomalous_update:
                # Implausible jump in progress or expenditure
                anom_type = rng.choice(["prog_jump", "exp_spike", "neg_progress"])
                if anom_type == "prog_jump":
                    phys_prog = min(100.0, phys_prog + rng.uniform(25, 40))
                elif anom_type == "exp_spike":
                    cum_exp += sanctioned * rng.uniform(0.25, 0.45)
                else:
                    phys_prog = max(0.0, phys_prog - rng.uniform(5, 15))
            else:
                phys_prog  = float(np.clip(frac * 100 + noise * 20, 0.0, 100.0))
                target_exp = frac * final_cost
                cum_exp    = float(np.clip(rng.normal(target_exp, target_exp * 0.06), 0.0, final_cost * 1.1))

            fin_prog = (cum_exp / sanctioned * 100) if sanctioned > 0 else 0.0

            # Revised cost leaks in after midpoint for overruns
            if is_overrun and j > n_updates // 2:
                revised_cost = float(rng.normal(final_cost, final_cost * 0.03))
                prev_revised_count += 1
            else:
                revised_cost = sanctioned

            # Expected completion leaks in after 1/3 of updates for delays
            if is_delayed and j > n_updates // 3:
                expected_completion = final_end
            else:
                expected_completion = planned_end

            # ── Milestone data ─────────────────────────────────────────────
            m_name    = milestone_names[j]
            m_planned = planned_start + timedelta(days=int(durations_days[i] * frac))
            m_exp     = expected_completion - timedelta(days=int((n_updates - j) * 30))

            # Milestone actual: completed if ahead or on time
            if phys_prog >= frac * 100:
                m_actual: str | None = upd_date.strftime("%Y-%m-%d")
            else:
                m_actual = None

            records.append({
                "project_id":                project_id,
                "update_date":               upd_date.strftime("%Y-%m-%d"),
                "ministry":                  ministry,
                "sector":                    sector,
                "agency":                    agency,
                "state":                     state,
                "sanctioned_cost":           round(sanctioned, 2),
                "planned_start":             planned_start.strftime("%Y-%m-%d"),
                "planned_end":               planned_end.strftime("%Y-%m-%d"),
                "project_type":              ptype,
                "physical_progress_pct":     round(phys_prog, 2),
                "financial_progress_pct":    round(fin_prog, 2),
                "cumulative_expenditure":    round(cum_exp, 2),
                "revised_cost":              round(revised_cost, 2),
                "expected_completion_date":  expected_completion.strftime("%Y-%m-%d"),
                "milestone_name":            m_name,
                "milestone_planned_date":    m_planned.strftime("%Y-%m-%d"),
                "milestone_expected_date":   m_exp.strftime("%Y-%m-%d"),
                "milestone_actual_date":     m_actual,
                # Outcome columns — present in every row but only used for labelling
                "final_cost":                round(final_cost, 2),
                "final_end_date":            final_end.strftime("%Y-%m-%d"),
                "delayed_flag":              int(is_delayed),
                "overrun_flag":              int(is_overrun),
                "outcome_known_at":          outcome_known_at.strftime("%Y-%m-%d"),
            })

    df = pd.DataFrame(records)
    return df


if __name__ == "__main__":
    import os

    output_path = "dataset.csv"
    df = generate_synthetic_data(num_projects=2000)
    df.to_csv(output_path, index=False)
    print(
        f"Generated {len(df):,} project-update records "
        f"across {df['project_id'].nunique():,} projects.\n"
        f"Saved to {os.path.abspath(output_path)}"
    )
