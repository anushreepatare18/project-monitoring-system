"""
PRAGYA AI — Anomaly Detector  (v2)
====================================
Secondary model: Isolation Forest trained on update-to-update deltas.
Complemented by rule-based checks for clear data-entry errors.

Outputs per-update:
  - anomaly_score  : float (lower = more anomalous; IF decision_function)
  - is_anomaly     : bool
  - anomaly_reason : str (human-readable, lists triggering fields)
"""
from __future__ import annotations

import os
import pickle
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

REGISTRY_DIR = Path("ml_core/registry")
MODEL_PATH   = str(REGISTRY_DIR / "anomaly_model.pkl")

# Delta features used by the Isolation Forest
DELTA_FEATURES = [
    "delta_physical",
    "delta_financial",
    "delta_expenditure",
]


# ── Delta computation ─────────────────────────────────────────────────────────

def compute_deltas(df_history: pd.DataFrame) -> pd.DataFrame:
    """
    Compute update-to-update deltas for every project update.
    Drops first update per project (no previous to diff against).
    """
    df = df_history.copy()
    df = df.sort_values(["project_id", "update_date"]).reset_index(drop=True)

    grp = df.groupby("project_id", sort=False)
    df["prev_physical"]     = grp["physical_progress_pct"].shift(1)
    df["prev_financial"]    = grp["financial_progress_pct"].shift(1)
    df["prev_expenditure"]  = grp["cumulative_expenditure"].shift(1)

    df["delta_physical"]    = df["physical_progress_pct"] - df["prev_physical"]
    df["delta_financial"]   = df["financial_progress_pct"] - df["prev_financial"]
    df["delta_expenditure"] = df["cumulative_expenditure"] - df["prev_expenditure"]

    # Drop first row per project (NaN deltas)
    return df.dropna(subset=["delta_physical"]).copy()


# ── Training ──────────────────────────────────────────────────────────────────

def train_anomaly_detector(
    data_path: str = "ml_core/data/synthetic_projects.csv",
) -> None:
    """Train the Isolation Forest on all update-to-update deltas and save it."""
    df     = pd.read_csv(data_path)
    deltas = compute_deltas(df)

    X = deltas[DELTA_FEATURES].fillna(0)
    iso = IsolationForest(
        n_estimators=200,
        contamination=0.05,
        max_samples="auto",
        random_state=42,
        n_jobs=-1,
    )
    iso.fit(X)

    REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
    with open(MODEL_PATH, "wb") as fh:
        pickle.dump(iso, fh)

    print(f"[anomaly] Isolation Forest trained on {len(X):,} deltas -> {MODEL_PATH}")


# ── Inference ─────────────────────────────────────────────────────────────────

def _load_model() -> Optional[IsolationForest]:
    if not os.path.exists(MODEL_PATH):
        return None
    with open(MODEL_PATH, "rb") as fh:
        return pickle.load(fh)


def _rule_based_reasons(row: pd.Series) -> list[str]:
    """
    Deterministic rule-based checks for obvious data-entry errors.
    Returns a list of reason strings (empty = no rule fired).
    """
    reasons: list[str] = []

    # Progress cannot drop by more than 5 percentage points in one update
    if row["delta_physical"] < -5:
        reasons.append(
            f"Implausible physical progress drop: "
            f"{row['delta_physical']:.1f} pp in one update."
        )

    # Financial progress cannot exceed physical by more than 20 pp
    if row["delta_financial"] - row["delta_physical"] > 20:
        reasons.append(
            f"Financial progress significantly outpaces physical progress "
            f"(gap: {row['delta_financial'] - row['delta_physical']:.1f} pp)."
        )

    # Expenditure spike: delta > 20 % of sanctioned cost in one period
    sc = row.get("sanctioned_cost", np.nan)
    if not np.isnan(sc) and sc > 0 and row["delta_expenditure"] > sc * 0.20:
        reasons.append(
            f"Sudden expenditure spike: ₹{row['delta_expenditure']:.1f} Cr "
            f"in one update ({row['delta_expenditure']/sc*100:.1f}% of sanctioned cost)."
        )

    # Progress cannot exceed 100 %
    if row["physical_progress_pct"] > 100:
        reasons.append(
            f"Physical progress exceeds 100% "
            f"({row['physical_progress_pct']:.1f}%)."
        )

    return reasons


def detect_anomalies(
    df_history: pd.DataFrame,
    as_of_date: Optional[str] = None,
) -> pd.DataFrame:
    """
    Detect anomalous project updates.

    Parameters
    ----------
    df_history : DataFrame
        Full update history for one or more projects.
    as_of_date : str, optional
        If provided, only updates on or before this date are considered.

    Returns
    -------
    DataFrame with original columns plus:
        anomaly_score, is_anomaly, anomaly_reason
    """
    iso = _load_model()

    df = df_history.copy()
    if as_of_date:
        df = df[pd.to_datetime(df["update_date"]) <= pd.to_datetime(as_of_date)]

    deltas = compute_deltas(df)
    if len(deltas) == 0:
        return pd.DataFrame()

    X = deltas[DELTA_FEATURES].fillna(0)

    if iso is not None:
        deltas["anomaly_score"] = iso.decision_function(X)
        deltas["is_anomaly"]    = iso.predict(X) == -1
    else:
        # Without a trained model, use a simple z-score fallback
        z = (X - X.mean()) / (X.std() + 1e-9)
        deltas["anomaly_score"] = -z.abs().max(axis=1)
        deltas["is_anomaly"]    = deltas["anomaly_score"] < -2.0

    reasons: list[str] = []
    for _, row in deltas.iterrows():
        rule_reasons = _rule_based_reasons(row)
        if rule_reasons:
            reasons.append(" | ".join(rule_reasons))
            deltas.loc[row.name, "is_anomaly"] = True   # rules override IF
        elif row["is_anomaly"]:
            reasons.append("Unusual combination of delta values detected by Isolation Forest.")
        else:
            reasons.append("")

    deltas["anomaly_reason"] = reasons
    return deltas


if __name__ == "__main__":
    train_anomaly_detector()
