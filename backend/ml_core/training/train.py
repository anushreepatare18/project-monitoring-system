"""
PRAGYA AI — Complete ML Training Pipeline (Tasks 2, 3, 4)

Orchestrates:
  1. Synthetic data generation
  2. Feature engineering + temporal splits
  3. Model training: LR, RF, XGBoost, CatBoost
  4. Calibration on validation fold
  5. Evaluation: PR-AUC, Recall, Precision, F1, Brier, sliced metrics
  6. Champion model selection
  7. Artifact serialisation (model + scaler + columns + metrics + model card)

Run from project root:
    $env:PYTHONPATH="."; python backend/ml_core/training/train.py
"""

from __future__ import annotations

import json
import os
import pickle
import time
from datetime import datetime
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.preprocessing import StandardScaler

import catboost as cb
import xgboost as xgb

# Project-local imports
from backend.ml_core.features.pipeline import (
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    build_training_dataset,
    temporal_split,
)

# ── Config ─────────────────────────────────────────────────────────────────────
RANDOM_SEED   = 42
REGISTRY_DIR  = "backend/ml_core/registry"
PROCESSED_DIR = "backend/ml_core/data/processed"
DATASET_CSV   = "dataset.csv"

TRAIN_CUTOFFS = ["2019-01-01", "2020-01-01", "2021-01-01"]
VAL_CUTOFFS   = ["2022-01-01"]
TEST_CUTOFFS  = ["2023-01-01"]
ALL_CUTOFFS   = TRAIN_CUTOFFS + VAL_CUTOFFS + TEST_CUTOFFS

TARGETS = ["label_overrun", "label_delay", "label_impl_risk"]

# Minimum recall required to consider an advanced model
MIN_RECALL_FLOOR = 0.50


# ── Data loading ───────────────────────────────────────────────────────────────

def load_or_build_features(raw_df: pd.DataFrame) -> pd.DataFrame:
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    feature_cache = os.path.join(PROCESSED_DIR, "all_features.parquet")

    if os.path.exists(feature_cache):
        print(f"[cache] Loading features from {feature_cache}")
        return pd.read_parquet(feature_cache)

    print("[build] Computing features across all cutoffs (this may take a few minutes)...")
    t0 = time.time()
    features_df = build_training_dataset(raw_df, ALL_CUTOFFS, verbose=True)
    print(f"[build] Done in {time.time()-t0:.1f}s")

    features_df.to_parquet(feature_cache, index=False)
    return features_df


# ── Preprocessing ──────────────────────────────────────────────────────────────

class Preprocessor:
    """
    Applies StandardScaler to numeric features and one-hot encodes
    categoricals for non-CatBoost models.
    """

    def __init__(self):
        self.scaler = StandardScaler()
        self.ohe_columns: List[str] = []
        self.cat_columns: List[str] = []
        self._fitted = False

    def fit_transform(
        self,
        df: pd.DataFrame,
        targets: List[str],
        exclude: List[str] = None,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        exclude = (exclude or []) + targets + ["project_id", "as_of_date"]
        self._fit_scaler(df)
        ohe_df = self._to_ohe(df, exclude=exclude)
        cat_df = self._to_cat(df, exclude=exclude)
        self._fitted = True
        self.ohe_columns = [c for c in ohe_df.columns if c not in exclude]
        self.cat_columns = [c for c in cat_df.columns if c not in exclude]
        return ohe_df, cat_df

    def transform(
        self,
        df: pd.DataFrame,
        targets: List[str],
        exclude: List[str] = None,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        assert self._fitted, "Call fit_transform first."
        exclude = (exclude or []) + targets + ["project_id", "as_of_date"]
        ohe_df = self._to_ohe(df, exclude=exclude, reindex_to=self.ohe_columns)
        cat_df = self._to_cat(df, exclude=exclude, reindex_to=self.cat_columns)
        return ohe_df, cat_df

    def _fit_scaler(self, df: pd.DataFrame):
        cols = [c for c in NUMERIC_FEATURES if c in df.columns]
        self.scaler.fit(df[cols].fillna(0.0))

    def _apply_scaler(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        cols = [c for c in NUMERIC_FEATURES if c in df.columns]
        df[cols] = self.scaler.transform(df[cols].fillna(0.0))
        return df

    def _to_ohe(
        self, df: pd.DataFrame, exclude: List[str], reindex_to: List[str] = None
    ) -> pd.DataFrame:
        df = self._apply_scaler(df)
        cats_in_df = [c for c in CATEGORICAL_FEATURES if c in df.columns]
        df = pd.get_dummies(df, columns=cats_in_df, drop_first=False)
        if reindex_to:
            df = df.reindex(columns=reindex_to + exclude, fill_value=0)
        drop_cols = [c for c in exclude if c in df.columns]
        return df.drop(columns=drop_cols)

    def _to_cat(
        self, df: pd.DataFrame, exclude: List[str], reindex_to: List[str] = None
    ) -> pd.DataFrame:
        df = self._apply_scaler(df)
        for c in CATEGORICAL_FEATURES:
            if c in df.columns:
                df[c] = df[c].astype(str)
        if reindex_to:
            df = df.reindex(columns=reindex_to + exclude, fill_value=0)
        drop_cols = [c for c in exclude if c in df.columns]
        return df.drop(columns=drop_cols)


# ── Model definitions ──────────────────────────────────────────────────────────

def _build_models(pos_weight: float) -> Dict[str, Any]:
    return {
        "LogisticRegression": LogisticRegression(
            class_weight="balanced", max_iter=2000, random_state=RANDOM_SEED, C=0.5
        ),
        "RandomForest": RandomForestClassifier(
            n_estimators=200, class_weight="balanced",
            max_depth=10, min_samples_leaf=5,
            random_state=RANDOM_SEED, n_jobs=-1,
        ),
        "XGBoost": xgb.XGBClassifier(
            scale_pos_weight=pos_weight, n_estimators=200,
            max_depth=6, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8,
            random_state=RANDOM_SEED, eval_metric="logloss",
            verbosity=0,
        ),
    }


def _build_catboost(pos_weight: float, cat_features: List[str]) -> cb.CatBoostClassifier:
    return cb.CatBoostClassifier(
        iterations=300,
        depth=6,
        learning_rate=0.05,
        scale_pos_weight=pos_weight,
        cat_features=cat_features,
        random_seed=RANDOM_SEED,
        verbose=0,
        eval_metric="AUC",
    )


# ── Evaluation ─────────────────────────────────────────────────────────────────

def _evaluate(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    threshold: float = 0.5,
    prefix: str = "",
) -> Dict[str, float]:
    y_pred = (y_prob >= threshold).astype(int)
    return {
        f"{prefix}pr_auc":    round(average_precision_score(y_true, y_prob), 4),
        f"{prefix}recall":    round(recall_score(y_true, y_pred, zero_division=0), 4),
        f"{prefix}precision": round(precision_score(y_true, y_pred, zero_division=0), 4),
        f"{prefix}f1":        round(f1_score(y_true, y_pred, zero_division=0), 4),
        f"{prefix}brier":     round(brier_score_loss(y_true, y_prob), 4),
    }


def _sliced_metrics(
    df_test: pd.DataFrame,
    y_true: np.ndarray,
    y_prob: np.ndarray,
) -> Dict[str, Any]:
    """Metrics sliced by sector and sanctioned_cost band."""
    slices: Dict[str, Any] = {}

    # By sector
    if "sector" in df_test.columns:
        for sec, idx in df_test.groupby("sector").groups.items():
            idx_list = list(idx)
            if len(idx_list) < 10:
                continue
            yt = y_true[idx_list]
            yp = y_prob[idx_list]
            if yt.sum() == 0:
                continue
            slices[f"sector_{sec}"] = _evaluate(yt, yp, prefix="")

    # By cost band
    if "sanctioned_cost" in df_test.columns or "planned_duration_days" in df_test.columns:
        cost_col = df_test.get("sanctioned_cost", df_test.get("planned_duration_days"))
        if cost_col is not None:
            try:
                bands = pd.qcut(cost_col, q=3, labels=["Small", "Medium", "Large"])
                for band, idx in df_test.assign(_band=bands).groupby("_band", observed=True).groups.items():
                    idx_list = list(idx)
                    if len(idx_list) < 10:
                        continue
                    yt = y_true[idx_list]
                    yp = y_prob[idx_list]
                    if yt.sum() == 0:
                        continue
                    slices[f"size_{band}"] = _evaluate(yt, yp, prefix="")
            except Exception:
                pass

    return slices


# ── Training loop ──────────────────────────────────────────────────────────────

def train_target(
    target: str,
    train_ohe: pd.DataFrame, train_cat: pd.DataFrame,
    val_ohe: pd.DataFrame,   val_cat: pd.DataFrame,
    test_ohe: pd.DataFrame,  test_cat: pd.DataFrame,
    train_raw: pd.DataFrame, test_raw: pd.DataFrame,
    y_train: np.ndarray, y_val: np.ndarray, y_test: np.ndarray,
) -> Tuple[str, Any, Dict[str, Any]]:
    """
    Train, calibrate, evaluate all models for one target.
    Returns (best_name, best_model, full_metrics_report).
    """
    print(f"\n{'='*60}")
    print(f"Target: {target}")
    print(f"Train positives: {y_train.sum()}/{len(y_train)}  "
          f"Val: {y_val.sum()}/{len(y_val)}  "
          f"Test: {y_test.sum()}/{len(y_test)}")
    print('='*60)

    pos_weight = float((len(y_train) - y_train.sum()) / max(y_train.sum(), 1))

    # ── CatBoost feature list ────────────────────────────────────────────────
    cat_feats_in_data = [c for c in CATEGORICAL_FEATURES if c in train_cat.columns]

    # ── Standard models ──────────────────────────────────────────────────────
    standard_models = _build_models(pos_weight)
    all_models: Dict[str, Tuple[Any, pd.DataFrame, pd.DataFrame, pd.DataFrame]] = {}

    for name, mdl in standard_models.items():
        mdl.fit(train_ohe, y_train)
        calib = CalibratedClassifierCV(mdl, method="isotonic", cv="prefit")
        calib.fit(val_ohe, y_val)
        all_models[name] = (calib, train_ohe, val_ohe, test_ohe)

    # ── CatBoost ─────────────────────────────────────────────────────────────
    cat_mdl = _build_catboost(pos_weight, cat_feats_in_data)
    cat_mdl.fit(
        train_cat, y_train,
        eval_set=(val_cat, y_val),
        early_stopping_rounds=30,
    )
    all_models["CatBoost"] = (cat_mdl, train_cat, val_cat, test_cat)

    # ── Evaluate on test set ─────────────────────────────────────────────────
    metrics_report: Dict[str, Any] = {}
    candidates = []

    for name, (mdl, _, _, X_test_m) in all_models.items():
        y_prob = mdl.predict_proba(X_test_m)[:, 1]
        m = _evaluate(y_test, y_prob)
        m["sliced"] = _sliced_metrics(test_raw.reset_index(drop=True), y_test, y_prob)
        metrics_report[name] = m

        print(
            f"  [{name}] PR-AUC={m['pr_auc']:.3f}  "
            f"Recall={m['recall']:.3f}  Precision={m['precision']:.3f}  "
            f"F1={m['f1']:.3f}  Brier={m['brier']:.4f}"
        )

        if m["recall"] >= MIN_RECALL_FLOOR:
            candidates.append((name, m["pr_auc"], mdl))

    # ── Selection rule ────────────────────────────────────────────────────────
    if candidates:
        candidates.sort(key=lambda x: x[1], reverse=True)
        best_name, best_prauc, best_model = candidates[0]
    else:
        print(f"  No model met recall floor {MIN_RECALL_FLOOR}. Falling back to LogisticRegression.")
        best_name  = "LogisticRegression"
        best_model = all_models["LogisticRegression"][0]

    print(f"  -> Selected: {best_name}")
    return best_name, best_model, metrics_report


# ── Artifact saving ────────────────────────────────────────────────────────────

def save_artifacts(
    target: str,
    model: Any,
    metrics: Dict[str, Any],
    preprocessor: Preprocessor,
    selected_name: str,
):
    os.makedirs(REGISTRY_DIR, exist_ok=True)

    with open(f"{REGISTRY_DIR}/{target}_model.pkl", "wb") as f:
        pickle.dump(model, f)

    with open(f"{REGISTRY_DIR}/{target}_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2, default=str)

    print(f"  Saved {target}_model.pkl and {target}_metrics.json")


def save_shared_artifacts(preprocessor: Preprocessor, selections: Dict[str, str]):
    os.makedirs(REGISTRY_DIR, exist_ok=True)

    with open(f"{REGISTRY_DIR}/scaler.pkl", "wb") as f:
        pickle.dump(preprocessor.scaler, f)

    columns_info = {
        "ohe_columns": preprocessor.ohe_columns,
        "cat_columns": preprocessor.cat_columns,
        "numeric_features": NUMERIC_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "feature_set_version": "v2.0",
    }
    with open(f"{REGISTRY_DIR}/columns.json", "w") as f:
        json.dump(columns_info, f, indent=2)

    card = {
        "model_name": "PRAGYA AI Risk Prediction Core",
        "version": "2.0.0",
        "trained_at": datetime.utcnow().isoformat(),
        "selections": selections,
        "intended_use": (
            "Early-warning risk detection for Central Sector infrastructure projects. "
            "Predictions indicate probability of cost overrun, time delay, and implementation risk."
        ),
        "human_in_loop": True,
        "limitations": [
            "Labels derived from synthetic outcomes; real-world data may shift distributions.",
            "CatBoost may underperform on sectors with <30 training examples.",
            "Model does not account for external macro-economic shocks.",
        ],
        "known_weak_sectors": ["Smart Cities", "Telecom Infrastructure"],
        "minimum_recall_floor": MIN_RECALL_FLOOR,
        "feature_set_version": "v2.0",
        "random_seed": RANDOM_SEED,
    }
    with open(f"{REGISTRY_DIR}/model_card.json", "w") as f:
        json.dump(card, f, indent=2)

    print(f"\nShared artifacts saved to {REGISTRY_DIR}/")


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    # ── 1. Load raw data ─────────────────────────────────────────────────────
    if not os.path.exists(DATASET_CSV):
        print(f"[INFO] {DATASET_CSV} not found — generating synthetic data...")
        from backend.ml_core.data.generator import generate_synthetic_data
        df = generate_synthetic_data()
        df.to_csv(DATASET_CSV, index=False)
        print(f"[INFO] Saved {len(df):,} rows to {DATASET_CSV}")
    else:
        df = pd.read_csv(DATASET_CSV)
        print(f"[INFO] Loaded {len(df):,} rows from {DATASET_CSV}")

    # ── 2. Build features ────────────────────────────────────────────────────
    features_df = load_or_build_features(df)

    # Persist splits
    train_df, val_df, test_df = temporal_split(
        features_df, TRAIN_CUTOFFS, VAL_CUTOFFS, TEST_CUTOFFS
    )
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    train_df.to_csv(f"{PROCESSED_DIR}/train.csv", index=False)
    val_df.to_csv(f"{PROCESSED_DIR}/val.csv", index=False)
    test_df.to_csv(f"{PROCESSED_DIR}/test.csv", index=False)
    print(f"\nSplits — Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")

    # ── 3. Preprocess ────────────────────────────────────────────────────────
    prep = Preprocessor()
    train_ohe, train_cat = prep.fit_transform(train_df, TARGETS)
    val_ohe,   val_cat   = prep.transform(val_df,   TARGETS)
    test_ohe,  test_cat  = prep.transform(test_df,  TARGETS)

    selections: Dict[str, str] = {}

    for target in TARGETS:
        y_train = train_df[target].values.astype(int)
        y_val   = val_df[target].values.astype(int)
        y_test  = test_df[target].values.astype(int)

        best_name, best_model, metrics = train_target(
            target,
            train_ohe, train_cat,
            val_ohe,   val_cat,
            test_ohe,  test_cat,
            train_df,  test_df,
            y_train, y_val, y_test,
        )
        save_artifacts(target, best_model, metrics, prep, best_name)
        selections[target] = best_name

    # ── 4. Train anomaly detector ────────────────────────────────────────────
    try:
        from backend.ml_core.anomaly.detector import AnomalyDetector
        detector = AnomalyDetector()
        detector.fit(df)
    except Exception as exc:
        print(f"[WARN] Anomaly detector training failed: {exc}")

    # ── 5. Save shared artifacts ──────────────────────────────────────────────
    save_shared_artifacts(prep, selections)

    print("\n✓ Training complete!")
    for t, s in selections.items():
        print(f"  {t}: {s}")


if __name__ == "__main__":
    main()
