"""
PRAGYA AI — Anomaly Detection (Task 6)

Two-stage anomaly system:
  Stage 1: Rule-based checks (fast, deterministic, human-readable triggers)
  Stage 2: Isolation Forest on update-to-update deltas (unsupervised ML)

Output: anomaly_score in [0, 1], flag, and list of specific trigger strings.
"""

from __future__ import annotations

import os
import pickle
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

REGISTRY_DIR = "backend/ml_core/registry"

# ── Delta feature extraction ──────────────────────────────────────────────────

DELTA_FEATURES = ["prog_velocity", "exp_velocity", "date_shift_days", "rev_cost_jump_pct"]


def _compute_deltas(project_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute update-to-update delta features for one project.

    Parameters
    ----------
    project_df : pd.DataFrame  sorted by update_date (ascending)

    Returns
    -------
    pd.DataFrame  with one row per consecutive pair (rows from index 1 onwards)
    """
    if len(project_df) < 2:
        return pd.DataFrame(columns=DELTA_FEATURES)

    df = project_df.copy().reset_index(drop=True)
    df["update_date"] = pd.to_datetime(df["update_date"])
    df["expected_completion_date"] = pd.to_datetime(
        df["expected_completion_date"], errors="coerce"
    )

    df["_days_gap"]   = df["update_date"].diff().dt.days.clip(lower=1)
    df["_prog_jump"]  = df["physical_progress_pct"].diff().fillna(0.0)
    df["_exp_spike"]  = df["cumulative_expenditure"].diff().fillna(0.0)
    df["_date_shift"] = df["expected_completion_date"].diff().dt.days.fillna(0.0)

    sanctioned = df["sanctioned_cost"].iloc[0]
    rev_prev   = df["revised_cost"].shift(1).fillna(df["revised_cost"])
    df["_rev_cost_jump_pct"] = (
        (df["revised_cost"] - rev_prev) / (sanctioned + 1e-9)
    ).fillna(0.0) * 100.0

    df["prog_velocity"] = df["_prog_jump"] / df["_days_gap"]
    df["exp_velocity"]  = df["_exp_spike"] / (sanctioned + 1e-9) * 100.0  # % of sanctioned per day
    df["date_shift_days"]   = df["_date_shift"]
    df["rev_cost_jump_pct"] = df["_rev_cost_jump_pct"]

    return df.iloc[1:][DELTA_FEATURES].fillna(0.0)


# ── Rule-based checks ─────────────────────────────────────────────────────────

def _rule_checks(
    project_df: pd.DataFrame,
) -> Tuple[float, List[str]]:
    """
    Apply hard rule-based anomaly checks.

    Returns (penalty_score_addition [0,1], list of trigger strings)
    """
    if project_df.empty:
        return 0.0, []

    df = project_df.sort_values("update_date").reset_index(drop=True)
    latest  = df.iloc[-1]
    prev    = df.iloc[-2] if len(df) >= 2 else None
    triggers: List[str] = []
    score = 0.0

    # Bounds checks
    phys = latest.get("physical_progress_pct", 0)
    if phys > 100:
        triggers.append(f"Physical progress {phys:.1f}% exceeds 100% — data entry error")
        score = max(score, 1.0)
    if phys < 0:
        triggers.append(f"Physical progress {phys:.1f}% is negative — data entry error")
        score = max(score, 1.0)

    sanc = float(latest.get("sanctioned_cost", 1) or 1)
    cum  = float(latest.get("cumulative_expenditure", 0) or 0)
    if cum > sanc * 2.5:
        triggers.append(
            f"Expenditure (₹{cum:.1f} Cr) is more than 2.5× the sanctioned cost (₹{sanc:.1f} Cr)"
        )
        score = max(score, 0.9)

    rev  = float(latest.get("revised_cost", sanc) or sanc)
    if rev > sanc * 3.0:
        triggers.append(
            f"Revised cost (₹{rev:.1f} Cr) exceeds 3× the sanctioned amount — implausible"
        )
        score = max(score, 0.85)

    # Jump checks (vs previous update)
    if prev is not None:
        prev_phys = float(prev.get("physical_progress_pct", 0) or 0)
        prog_jump = phys - prev_phys
        if prog_jump > 30:
            triggers.append(
                f"Physical progress jumped {prog_jump:.1f}% in one update — implausible"
            )
            score = max(score, 0.80)
        if prog_jump < -10:
            triggers.append(
                f"Physical progress regressed {abs(prog_jump):.1f}% — negative progress reported"
            )
            score = max(score, 0.75)

        prev_cum = float(prev.get("cumulative_expenditure", 0) or 0)
        exp_jump = cum - prev_cum
        if exp_jump > sanc * 0.30:
            triggers.append(
                f"Expenditure spiked by ₹{exp_jump:.1f} Cr (>{30:.0f}% of sanctioned) in one update"
            )
            score = max(score, 0.75)

    # Staleness check
    try:
        last_upd = pd.Timestamp(latest.get("update_date", "2000-01-01"))
        days_stale = (pd.Timestamp.today() - last_upd).days
        if days_stale > 180:
            triggers.append(f"No update received for {days_stale} days — project may be stalled")
            score = max(score, 0.55)
    except Exception:
        pass

    # Completion date in the past with unfinished progress
    try:
        exp_comp = pd.Timestamp(latest.get("expected_completion_date", "2099-01-01"))
        if exp_comp < pd.Timestamp.today() and phys < 95:
            triggers.append(
                f"Expected completion date ({exp_comp.date()}) has passed but project is only "
                f"{phys:.1f}% complete"
            )
            score = max(score, 0.65)
    except Exception:
        pass

    return float(score), triggers


# ── Anomaly Detector class ─────────────────────────────────────────────────────

class AnomalyDetector:
    """
    Two-stage anomaly detector.

    fit(df) — trains IsolationForest on full dataset deltas.
    detect(project_df) → (is_anomalous, score, triggers)
    """

    def __init__(self, random_state: int = 42, contamination: float = 0.05):
        self.iso_forest = IsolationForest(
            n_estimators=200,
            contamination=contamination,
            random_state=random_state,
            n_jobs=-1,
        )
        self.is_fitted = False
        self._training_scale: Dict[str, float] = {}

    # ── Training ─────────────────────────────────────────────────────────────

    def fit(self, df: pd.DataFrame) -> "AnomalyDetector":
        """
        Train IsolationForest on update-to-update deltas across all projects.
        """
        df = df.copy()
        df["update_date"] = pd.to_datetime(df["update_date"])

        all_deltas: List[pd.DataFrame] = []
        for _pid, grp in df.groupby("project_id"):
            grp_sorted = grp.sort_values("update_date")
            d = _compute_deltas(grp_sorted)
            if not d.empty:
                all_deltas.append(d)

        if not all_deltas:
            print("[WARN] No delta data available for anomaly detector training.")
            return self

        full = pd.concat(all_deltas, ignore_index=True).fillna(0.0)

        # Store scale for score normalisation
        for col in DELTA_FEATURES:
            self._training_scale[col] = float(full[col].std() or 1.0)

        self.iso_forest.fit(full[DELTA_FEATURES])
        self.is_fitted = True

        os.makedirs(REGISTRY_DIR, exist_ok=True)
        with open(f"{REGISTRY_DIR}/anomaly_detector.pkl", "wb") as f:
            pickle.dump(self, f)

        print(
            f"[AnomalyDetector] Trained on {len(full):,} delta rows "
            f"from {df['project_id'].nunique():,} projects. Saved to registry."
        )
        return self

    # ── Inference ────────────────────────────────────────────────────────────

    def detect(
        self, project_df: pd.DataFrame
    ) -> Tuple[bool, float, List[str]]:
        """
        Run anomaly detection on a project's update history.

        Parameters
        ----------
        project_df : pd.DataFrame
            All update rows for ONE project (unsorted).

        Returns
        -------
        Tuple[bool, float, list[str]]
            is_anomalous : True if flagged
            score        : normalised anomaly severity [0, 1]
            triggers     : list of human-readable trigger descriptions
        """
        if project_df.empty:
            return False, 0.0, []

        df_sorted = project_df.sort_values("update_date").reset_index(drop=True)

        # ── Stage 1: Rules ────────────────────────────────────────────────
        rule_score, triggers = _rule_checks(df_sorted)

        # ── Stage 2: ML (if fitted and ≥2 updates) ───────────────────────
        ml_score = 0.0
        if self.is_fitted and len(df_sorted) >= 2:
            deltas = _compute_deltas(df_sorted)
            if not deltas.empty:
                latest_delta = deltas.iloc[[-1]][DELTA_FEATURES].fillna(0.0)
                raw_score = self.iso_forest.score_samples(latest_delta)[0]
                # score_samples returns negative; lower = more anomalous
                # Typical range roughly -0.9 to -0.1
                ml_score = float(np.clip((-raw_score - 0.1) / 0.8, 0.0, 1.0))

                if ml_score > 0.55:
                    # Identify which delta feature is most extreme
                    row = latest_delta.iloc[0]
                    for col in DELTA_FEATURES:
                        scale = self._training_scale.get(col, 1.0)
                        if abs(row[col]) > 3.0 * scale:
                            triggers.append(f"Statistical outlier in '{col}' (ML-detected)")

        # ── Combine ───────────────────────────────────────────────────────
        combined_score = float(max(rule_score, ml_score * 0.7))
        is_anomalous   = combined_score > 0.40 or len(triggers) > 0

        return is_anomalous, round(combined_score, 4), list(set(triggers))


# ── Module-level helper ────────────────────────────────────────────────────────

def load_detector() -> Optional[AnomalyDetector]:
    path = f"{REGISTRY_DIR}/anomaly_detector.pkl"
    if os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    return None


if __name__ == "__main__":
    import sys

    csv_path = sys.argv[1] if len(sys.argv) > 1 else "dataset.csv"
    print(f"Training anomaly detector on {csv_path} ...")
    try:
        df = pd.read_csv(csv_path)
        detector = AnomalyDetector()
        detector.fit(df)
    except Exception as exc:
        print(f"Failed: {exc}")
