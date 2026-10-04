"""
PRAGYA AI — Model Training, Calibration & Evaluation  (v2)
===========================================================
Trains Logistic Regression, Random Forest, XGBoost, CatBoost for each of
three targets:
  - overrun_flag         (cost overrun)
  - delayed_flag         (time delay)
  - implementation_risk_flag (milestone stagnation / high-delay ratio)

Uses strict time-based splits (train -> val -> test). No random shuffling.
Saves best model + full metrics + model card to ml_core/registry/.
"""
from __future__ import annotations

import json
import os
import pickle
import warnings
from datetime import date
from pathlib import Path
from typing import Optional, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from sklearn.calibration import calibration_curve
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBClassifier

from ml_core.features.pipeline import (
    ALL_FEATURES,
    CATEGORICAL_FEATURES,
    FEATURE_SET_VERSION,
    NUMERIC_FEATURES,
    compute_features,
)

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

# ── Paths ─────────────────────────────────────────────────────────────────────
REGISTRY_DIR = Path("ml_core/registry")
REGISTRY_DIR.mkdir(parents=True, exist_ok=True)

MODEL_VERSION  = "v2.0.0"
RANDOM_SEED    = 42
MIN_RECALL_FLOOR = 0.45
THRESHOLD      = 0.40


class CalibratedWrapper:
    """
    Module-level wrapper that pairs a fitted base model with an isotonic
    calibrator. Must be at module scope so pickle can serialise it.
    """
    def __init__(self, base, calibrator):
        self._base = base
        self._iso  = calibrator

    def predict_proba(self, X):
        raw = self._base.predict_proba(X)[:, 1]
        cal = np.clip(self._iso.predict(raw), 0.0, 1.0)
        return np.column_stack([1.0 - cal, cal])


# ── Time-based splits ─────────────────────────────────────────────────────────

def create_time_splits(
    df: pd.DataFrame,
    train_frac: float = 0.60,
    val_frac: float   = 0.20,
) -> Tuple[
    Tuple[pd.DataFrame, str],
    Tuple[pd.DataFrame, str],
    Tuple[pd.DataFrame, str],
]:
    """
    Split the dataset by outcome_known_at (temporal ordering).
    Returns (train_df, train_cutoff), (val_df, val_cutoff), (test_df, test_cutoff).
    No project leaks across train / test for the same prediction horizon.
    """
    df = df.copy()
    df["outcome_known_at"] = pd.to_datetime(df["outcome_known_at"])

    # Use the latest update per project as the representative row
    latest = (
        df.sort_values(["project_id", "update_date"])
          .groupby("project_id")
          .tail(1)
          .sort_values("outcome_known_at")
          .reset_index(drop=True)
    )

    n = len(latest)
    train_end = int(n * train_frac)
    val_end   = int(n * (train_frac + val_frac))

    train_pids = set(latest.iloc[:train_end]["project_id"])
    val_pids   = set(latest.iloc[train_end:val_end]["project_id"])
    test_pids  = set(latest.iloc[val_end:]["project_id"])

    # Hard check: no overlap between train and test
    assert not (train_pids & test_pids), "Project leaked between train and test!"
    assert not (val_pids & test_pids),   "Project leaked between val and test!"

    train_df = df[df["project_id"].isin(train_pids)].copy()
    val_df   = df[df["project_id"].isin(val_pids)].copy()
    test_df  = df[df["project_id"].isin(test_pids)].copy()

    train_cutoff = pd.to_datetime(
        latest.iloc[train_end - 1]["outcome_known_at"]
    ).strftime("%Y-%m-%d")
    val_cutoff = pd.to_datetime(
        latest.iloc[val_end - 1]["outcome_known_at"]
    ).strftime("%Y-%m-%d")
    test_cutoff = "2040-01-01"   # beyond all synthetic dates

    print(
        f"  Split sizes — Train: {len(train_pids)}, "
        f"Val: {len(val_pids)}, Test: {len(test_pids)} projects"
    )
    print(
        f"  Cutoffs — Train <= {train_cutoff} | "
        f"Val <= {val_cutoff} | Test <= {test_cutoff}"
    )
    return (train_df, train_cutoff), (val_df, val_cutoff), (test_df, test_cutoff)


# ── Preprocessing ─────────────────────────────────────────────────────────────

def build_sklearn_preprocessor() -> ColumnTransformer:
    """Build the column transformer for sklearn-based models."""
    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERIC_FEATURES),
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                CATEGORICAL_FEATURES,
            ),
        ],
        remainder="drop",
    )


# ── Evaluation helpers ────────────────────────────────────────────────────────

def evaluate_model(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    threshold: float = THRESHOLD,
) -> dict:
    """Compute evaluation metrics at the given operating threshold."""
    y_pred = (y_prob >= threshold).astype(int)
    return {
        "pr_auc":     float(average_precision_score(y_true, y_prob)),
        "roc_auc":    float(roc_auc_score(y_true, y_prob)),
        "brier_score": float(brier_score_loss(y_true, y_prob)),
        "precision":  float(precision_score(y_true, y_pred, zero_division=0)),
        "recall":     float(recall_score(y_true, y_pred, zero_division=0)),
        "f1":         float(f1_score(y_true, y_pred, zero_division=0)),
        "threshold":  threshold,
        "n_samples":  int(len(y_true)),
        "n_positives": int(y_true.sum()),
    }


def evaluate_by_sector(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    sectors: np.ndarray,
    threshold: float = THRESHOLD,
) -> dict[str, dict]:
    """Compute per-sector metrics."""
    results: dict[str, dict] = {}
    unique_sectors = np.unique(sectors)
    for s in unique_sectors:
        mask = sectors == s
        if mask.sum() < 10:
            continue
        results[s] = evaluate_model(y_true[mask], y_prob[mask], threshold)
    return results


def save_calibration_plot(
    y_true: np.ndarray, y_prob: np.ndarray, name: str, target: str
) -> str:
    frac_pos, mean_pred = calibration_curve(
        y_true, y_prob, n_bins=10, strategy="quantile"
    )
    path = str(REGISTRY_DIR / f"{target}_{name}_calibration.png")
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(mean_pred, frac_pos, marker="o", label=name)
    ax.plot([0, 1], [0, 1], "k--", label="Perfect calibration")
    ax.set_xlabel("Mean Predicted Probability")
    ax.set_ylabel("Fraction of Positives")
    ax.set_title(f"Calibration Reliability — {name} ({target})")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=100)
    plt.close(fig)
    return path


def save_pr_curve(
    y_true: np.ndarray, y_prob: np.ndarray, name: str, target: str
) -> str:
    prec, rec, _ = precision_recall_curve(y_true, y_prob)
    pr_auc       = average_precision_score(y_true, y_prob)
    path = str(REGISTRY_DIR / f"{target}_{name}_pr_curve.png")
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(rec, prec, label=f"PR-AUC = {pr_auc:.3f}")
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.set_title(f"Precision-Recall Curve — {name} ({target})")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=100)
    plt.close(fig)
    return path


# ── Rolling-origin backtest ───────────────────────────────────────────────────

def rolling_origin_backtest(
    df: pd.DataFrame,
    target: str,
    n_cutoffs: int = 3,
) -> list[dict]:
    """
    Perform a rolling-origin backtest with `n_cutoffs` expanding windows.
    Returns list of metric dicts (one per cutoff).
    """
    df = df.copy()
    df["outcome_known_at"] = pd.to_datetime(df["outcome_known_at"])
    latest = (
        df.sort_values(["project_id", "update_date"])
          .groupby("project_id")
          .tail(1)
          .sort_values("outcome_known_at")
          .reset_index(drop=True)
    )
    n = len(latest)

    backtest_results = []
    # Generate n_cutoffs equally spaced splits in [50%..80%] of the sorted data
    cutoff_fracs = np.linspace(0.50, 0.80, n_cutoffs)

    for frac in cutoff_fracs:
        split_at = int(n * frac)
        test_start = int(n * (frac + 0.10))
        if test_start >= n:
            continue

        train_pids = set(latest.iloc[:split_at]["project_id"])
        test_pids  = set(latest.iloc[test_start:min(n, test_start + 200)]["project_id"])
        if not test_pids:
            continue

        train_data = df[df["project_id"].isin(train_pids)]
        test_data  = df[df["project_id"].isin(test_pids)]

        train_cutoff = pd.to_datetime(
            latest.iloc[split_at - 1]["outcome_known_at"]
        ).strftime("%Y-%m-%d")
        test_cutoff = "2040-01-01"

        try:
            X_tr = compute_features(train_data, train_cutoff).reset_index()
            tr_pids = X_tr["project_id"].values
            X_tr = X_tr.drop(columns=["project_id"])
            y_tr = (
                train_data.drop_duplicates("project_id")
                          .set_index("project_id")
                          .loc[tr_pids, target]
                          .values
            )

            X_te = compute_features(test_data, test_cutoff).reset_index()
            te_pids = X_te["project_id"].values
            X_te = X_te.drop(columns=["project_id"])
            y_te = (
                test_data.drop_duplicates("project_id")
                         .set_index("project_id")
                         .loc[te_pids, target]
                         .values
            )

            if y_tr.sum() < 5 or y_te.sum() < 2:
                continue

            pipe = Pipeline([
                ("prep", build_sklearn_preprocessor()),
                ("clf",  RandomForestClassifier(
                    n_estimators=100, class_weight="balanced",
                    random_state=RANDOM_SEED, n_jobs=-1,
                )),
            ])
            pipe.fit(X_tr, y_tr)
            y_prob = pipe.predict_proba(X_te)[:, 1]
            metrics = evaluate_model(y_te, y_prob)
            metrics["cutoff"] = train_cutoff
            backtest_results.append(metrics)
        except Exception as e:
            print(f"  [backtest] Cutoff {train_cutoff} skipped: {e}")

    return backtest_results


# ── Main training function ────────────────────────────────────────────────────

def train_and_evaluate(
    target: str = "overrun_flag",
    data_path: str = "ml_core/data/synthetic_projects.csv",
) -> dict:
    """
    Train all four model types for `target`, select the best, calibrate,
    save to registry, and return the full results dict.
    """
    print(f"\n{'='*60}")
    print(f"  Training models for target: [{target}]")
    print(f"{'='*60}")

    df = pd.read_csv(data_path)
    df["update_date"]     = pd.to_datetime(df["update_date"])
    df["outcome_known_at"] = pd.to_datetime(df["outcome_known_at"])

    if target not in df.columns:
        raise ValueError(f"Target column '{target}' not found in dataset.")

    (train_df, train_cut), (val_df, val_cut), (test_df, test_cut) = \
        create_time_splits(df)

    def make_xy(
        split_df: pd.DataFrame, cutoff: str
    ) -> Tuple[pd.DataFrame, np.ndarray, np.ndarray]:
        X = compute_features(split_df, cutoff).reset_index()
        pids = X["project_id"].values
        X = X.drop(columns=["project_id"])
        labels = (
            split_df.drop_duplicates("project_id")
                    .set_index("project_id")
                    .loc[pids, target]
                    .values
        )
        return X, labels, pids

    X_train, y_train, _          = make_xy(train_df, train_cut)
    X_val,   y_val,   _          = make_xy(val_df,   val_cut)
    X_test,  y_test,  test_pids  = make_xy(test_df,  test_cut)

    pos_weight = max(1.0, (len(y_train) - sum(y_train)) / max(1, sum(y_train)))
    print(f"  Train: {len(y_train):,}  "
          f"({y_train.mean():.1%} +ve)  |  "
          f"Val: {len(y_val):,}  "
          f"({y_val.mean():.1%} +ve)  |  "
          f"Test: {len(y_test):,}  "
          f"({y_test.mean():.1%} +ve)")

    # ── Candidate models ──────────────────────────────────────────────────────
    candidates = {
        "LogisticRegression": Pipeline([
            ("prep", build_sklearn_preprocessor()),
            ("clf",  LogisticRegression(
                class_weight="balanced", max_iter=2000,
                random_state=RANDOM_SEED, C=1.0,
            )),
        ]),
        "RandomForest": Pipeline([
            ("prep", build_sklearn_preprocessor()),
            ("clf",  RandomForestClassifier(
                n_estimators=200, class_weight="balanced",
                random_state=RANDOM_SEED, n_jobs=-1,
            )),
        ]),
        "XGBoost": Pipeline([
            ("prep", build_sklearn_preprocessor()),
            ("clf",  XGBClassifier(
                n_estimators=300, scale_pos_weight=pos_weight,
                learning_rate=0.05, max_depth=5,
                random_state=RANDOM_SEED, eval_metric="logloss",
                verbosity=0,
            )),
        ]),
        "CatBoost": CatBoostClassifier(
            cat_features=CATEGORICAL_FEATURES,
            auto_class_weights="Balanced",
            iterations=300, learning_rate=0.05, depth=6,
            random_seed=RANDOM_SEED, verbose=0,
        ),
    }

    all_results: dict[str, dict] = {}
    best_name:  Optional[str]    = None
    best_model                   = None
    best_pr_auc: float           = -1.0

    for name, model in candidates.items():
        print(f"\n  > Training {name} …")

        model.fit(X_train, y_train)
        # Isotonic calibration on validation fold (sklearn 1.9 compatible)
        raw_val_prob  = model.predict_proba(X_val)[:, 1]
        raw_test_prob = model.predict_proba(X_test)[:, 1]
        iso = IsotonicRegression(out_of_bounds="clip")
        iso.fit(raw_val_prob, y_val)
        y_val_prob  = np.clip(iso.predict(raw_val_prob),  0, 1)
        y_test_prob = np.clip(iso.predict(raw_test_prob), 0, 1)

        calibrated = CalibratedWrapper(model, iso)

        val_metrics  = evaluate_model(y_val,  y_val_prob)
        test_metrics = evaluate_model(y_test, y_test_prob)

        # Sector-sliced test metrics
        sectors_test = np.array([
            test_df[test_df["project_id"] == pid]["sector"].iloc[0]
            for pid in test_pids
        ])
        test_metrics["by_sector"] = evaluate_by_sector(
            y_test, y_test_prob, sectors_test
        )

        all_results[name] = {"val": val_metrics, "test": test_metrics}

        print(
            f"    Val  — PR-AUC: {val_metrics['pr_auc']:.3f}  "
            f"Recall: {val_metrics['recall']:.3f}  "
            f"F1: {val_metrics['f1']:.3f}"
        )
        print(
            f"    Test — PR-AUC: {test_metrics['pr_auc']:.3f}  "
            f"Recall: {test_metrics['recall']:.3f}  "
            f"F1: {test_metrics['f1']:.3f}"
        )

        # Save diagnostic plots
        save_calibration_plot(y_test, y_test_prob, name, target)
        save_pr_curve(y_test, y_test_prob, name, target)

        # Model selection: best val PR-AUC subject to recall floor
        if (
            val_metrics["recall"] >= MIN_RECALL_FLOOR
            and val_metrics["pr_auc"] > best_pr_auc
        ):
            best_pr_auc = val_metrics["pr_auc"]
            best_name   = name
            best_model  = calibrated

    # Fallback: if no model met the recall floor, keep Logistic Regression
    if best_model is None:
        print(
            f"\n  [!] No model met recall floor {MIN_RECALL_FLOOR}. "
            "Keeping LogisticRegression baseline."
        )
        best_name = "LogisticRegression"
        lr_pipe   = candidates["LogisticRegression"]
        lr_pipe.fit(X_train, y_train)
        raw_val  = lr_pipe.predict_proba(X_val)[:, 1]
        raw_test = lr_pipe.predict_proba(X_test)[:, 1]
        iso_fb = IsotonicRegression(out_of_bounds="clip")
        iso_fb.fit(raw_val, y_val)

        best_model = CalibratedWrapper(lr_pipe, iso_fb)
        best_pr_auc = all_results.get("LogisticRegression", {}).get(
            "val", {}
        ).get("pr_auc", 0.0)

    print(f"\n  [OK] Selected [{target}]: {best_name}  "
          f"(Val PR-AUC = {best_pr_auc:.3f})")

    # ── Rolling-origin backtest ────────────────────────────────────────────────
    print("  Running rolling-origin backtest (3 cutoffs) …")
    backtest = rolling_origin_backtest(df, target, n_cutoffs=3)
    print(f"  Backtest PR-AUCs: {[round(r['pr_auc'], 3) for r in backtest]}")

    # ── Save model artefacts ──────────────────────────────────────────────────
    model_path = str(REGISTRY_DIR / f"{target}_best_model.pkl")
    with open(model_path, "wb") as fh:
        pickle.dump({
            "model":               best_model,
            "model_name":          best_name,
            "model_version":       MODEL_VERSION,
            "feature_set_version": FEATURE_SET_VERSION,
            "target":              target,
        }, fh)

    metrics_payload = {
        "target":              target,
        "selected_model":      best_name,
        "model_version":       MODEL_VERSION,
        "feature_set_version": FEATURE_SET_VERSION,
        "val_pr_auc":          best_pr_auc,
        "threshold":           THRESHOLD,
        "min_recall_floor":    MIN_RECALL_FLOOR,
        "all_results":         _strip_by_sector(all_results),   # JSON-safe
        "backtest":            backtest,
        "trained_on":          str(date.today()),
    }
    metrics_path = str(REGISTRY_DIR / f"{target}_metrics.json")
    with open(metrics_path, "w") as fh:
        json.dump(metrics_payload, fh, indent=2, default=str)

    # ── Model card ────────────────────────────────────────────────────────────
    card = {
        "model_name":       best_name,
        "target":           target,
        "version":          MODEL_VERSION,
        "feature_set_version": FEATURE_SET_VERSION,
        "intended_use": (
            "Early-warning risk prediction for government project monitoring officers. "
            "Human officers must verify every prediction before taking action."
        ),
        "limitations": (
            "Trained on synthetic data. Performance on real-world data may differ. "
            "Always verify predictions with domain experts."
        ),
        "known_weak_sectors": (
            "Sectors with fewer than 30 training projects may have lower accuracy. "
            "Check per-sector metrics in the metrics JSON."
        ),
        "training_date_range": (
            f"{train_df['update_date'].min().date()} "
            f"to {train_df['update_date'].max().date()}"
        ),
        "test_date_range": (
            f"{test_df['update_date'].min().date()} "
            f"to {test_df['update_date'].max().date()}"
        ),
        "metrics_test": _strip_by_sector(
            {best_name: all_results.get(best_name, {})}
        ).get(best_name, {}).get("test", {}),
        "trained_on": str(date.today()),
    }
    card_path = str(REGISTRY_DIR / f"{target}_model_card.json")
    with open(card_path, "w") as fh:
        json.dump(card, fh, indent=2, default=str)

    print(f"  Saved model   -> {model_path}")
    print(f"  Saved metrics -> {metrics_path}")
    print(f"  Saved card    -> {card_path}")

    return all_results


def _strip_by_sector(results: dict) -> dict:
    """
    Remove nested 'by_sector' dicts before JSON serialisation
    (kept in memory but too verbose for the summary JSON).
    """
    import copy
    out = copy.deepcopy(results)
    for model_name, splits in out.items():
        for split_name, metrics in splits.items():
            if isinstance(metrics, dict):
                metrics.pop("by_sector", None)
    return out


# ── CLI entry point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    for t in ["overrun_flag", "delayed_flag", "implementation_risk_flag"]:
        train_and_evaluate(t)
