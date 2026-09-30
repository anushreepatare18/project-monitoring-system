"""
PRAGYA XAI — /training/train.py
Train + compare + calibrate + evaluate all 4 model types for
delay and overrun targets. Save models, metrics, and comparison plots.

Run:
    $env:PYTHONPATH="."; python backend/pragya_xai/training/train.py
"""
from __future__ import annotations

import json
import os
import pickle
import time
from datetime import datetime
from typing import Any, Dict, List, Tuple

import matplotlib
matplotlib.use("Agg")   # headless — no GUI needed
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    PrecisionRecallDisplay,
    average_precision_score,
    brier_score_loss,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.preprocessing import StandardScaler
import catboost as cb
import xgboost as xgb

from backend.pragya_xai.features.pipeline import (
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    build_training_dataset,
)

# ── Paths ───────────────────────────────────────────────────────────────────────
ROOT         = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
MODEL_STORE  = os.path.join(ROOT, "backend", "pragya_xai", "model_store")
OUTPUTS_DIR  = os.path.join(ROOT, "backend", "pragya_xai", "outputs")
DATASET_CSV  = os.path.join(ROOT, "dataset.csv")
PROCESSED    = os.path.join(ROOT, "backend", "pragya_xai", "outputs", "processed")

TRAIN_CUTOFFS = ["2019-01-01", "2020-01-01", "2021-01-01"]
VAL_CUTOFFS   = ["2022-01-01"]
TEST_CUTOFFS  = ["2023-01-01"]
TARGETS       = ["label_overrun", "label_delay"]
SEED          = 42
MIN_RECALL    = 0.50

os.makedirs(MODEL_STORE, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)
os.makedirs(PROCESSED, exist_ok=True)


# ── Preprocessing ───────────────────────────────────────────────────────────────

class XAIPreprocessor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.ohe_cols: List[str] = []
        self.cat_cols: List[str] = []

    def fit_transform(self, df: pd.DataFrame, drop_cols: List[str]) -> Tuple[pd.DataFrame, pd.DataFrame]:
        num_cols = [c for c in NUMERIC_FEATURES if c in df.columns]
        self.scaler.fit(df[num_cols].fillna(0))
        return self._ohe(df, drop_cols, fit=True), self._cat(df, drop_cols, fit=True)

    def transform(self, df: pd.DataFrame, drop_cols: List[str]) -> Tuple[pd.DataFrame, pd.DataFrame]:
        return self._ohe(df, drop_cols), self._cat(df, drop_cols)

    def _scale(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        cols = [c for c in NUMERIC_FEATURES if c in df.columns]
        df[cols] = self.scaler.transform(df[cols].fillna(0))
        return df

    def _ohe(self, df: pd.DataFrame, drop_cols: List[str], fit: bool = False) -> pd.DataFrame:
        df = self._scale(df)
        cats = [c for c in CATEGORICAL_FEATURES if c in df.columns]
        df = pd.get_dummies(df, columns=cats, drop_first=False)
        if fit:
            self.ohe_cols = [c for c in df.columns if c not in drop_cols]
        df = df.reindex(columns=self.ohe_cols + drop_cols, fill_value=0)
        return df.drop(columns=[c for c in drop_cols if c in df.columns])

    def _cat(self, df: pd.DataFrame, drop_cols: List[str], fit: bool = False) -> pd.DataFrame:
        df = self._scale(df)
        for c in CATEGORICAL_FEATURES:
            if c in df.columns:
                df[c] = df[c].astype(str)
        if fit:
            self.cat_cols = [c for c in df.columns if c not in drop_cols]
        df = df.reindex(columns=self.cat_cols + drop_cols, fill_value=0)
        return df.drop(columns=[c for c in drop_cols if c in df.columns])


# ── Model builders ───────────────────────────────────────────────────────────────

def _models(pos_w: float) -> Dict[str, Any]:
    return {
        "LogisticRegression": LogisticRegression(
            class_weight="balanced", max_iter=3000, C=0.5, random_state=SEED
        ),
        "RandomForest": RandomForestClassifier(
            n_estimators=200, class_weight="balanced",
            max_depth=10, min_samples_leaf=5,
            random_state=SEED, n_jobs=-1,
        ),
        "XGBoost": xgb.XGBClassifier(
            scale_pos_weight=pos_w, n_estimators=200, max_depth=6,
            learning_rate=0.05, subsample=0.8, colsample_bytree=0.8,
            random_state=SEED, verbosity=0, eval_metric="logloss",
        ),
    }


def _catboost(pos_w: float, cat_feats: List[str]) -> cb.CatBoostClassifier:
    return cb.CatBoostClassifier(
        iterations=300, depth=6, learning_rate=0.05,
        scale_pos_weight=pos_w, cat_features=cat_feats,
        random_seed=SEED, verbose=0, eval_metric="AUC",
    )


# ── Evaluation ────────────────────────────────────────────────────────────────────

def _eval(y_true: np.ndarray, y_prob: np.ndarray, thr: float = 0.5) -> Dict[str, float]:
    y_hat = (y_prob >= thr).astype(int)
    return {
        "pr_auc":    round(average_precision_score(y_true, y_prob), 4),
        "recall":    round(recall_score(y_true, y_hat, zero_division=0), 4),
        "precision": round(precision_score(y_true, y_hat, zero_division=0), 4),
        "f1":        round(f1_score(y_true, y_hat, zero_division=0), 4),
        "brier":     round(brier_score_loss(y_true, y_prob), 4),
    }


def _save_comparison_table(results: Dict[str, Dict], target: str):
    rows = []
    for name, m in results.items():
        rows.append({
            "Model": name,
            "PR-AUC":    m["pr_auc"],
            "Recall":    m["recall"],
            "Precision": m["precision"],
            "F1":        m["f1"],
            "Brier":     m["brier"],
        })
    df = pd.DataFrame(rows).sort_values("PR-AUC", ascending=False)
    path = os.path.join(OUTPUTS_DIR, f"{target}_comparison.csv")
    df.to_csv(path, index=False)
    print(f"  Saved comparison table: {path}")
    return df


def _save_pr_curves(
    model_probs: Dict[str, np.ndarray],
    y_test: np.ndarray,
    target: str,
):
    fig, ax = plt.subplots(figsize=(8, 6))
    for name, y_prob in model_probs.items():
        disp = PrecisionRecallDisplay.from_predictions(
            y_test, y_prob,
            name=f"{name} (AUC={average_precision_score(y_test, y_prob):.3f})",
            ax=ax,
        )
    ax.set_title(f"PR Curve — {target}", fontsize=14)
    ax.legend(loc="upper right", fontsize=9)
    fig.tight_layout()
    path = os.path.join(OUTPUTS_DIR, f"{target}_pr_curves.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved PR curves: {path}")


def _save_bar_comparison(results: Dict[str, Dict], target: str):
    names  = list(results.keys())
    praucs = [results[n]["pr_auc"] for n in names]
    recalls= [results[n]["recall"] for n in names]

    x = np.arange(len(names))
    width = 0.35
    fig, ax = plt.subplots(figsize=(9, 5))
    bars1 = ax.bar(x - width/2, praucs,  width, label="PR-AUC",  color="#4C72B0", alpha=0.85)
    bars2 = ax.bar(x + width/2, recalls, width, label="Recall",  color="#DD8452", alpha=0.85)

    ax.set_xticks(x)
    ax.set_xticklabels(names, fontsize=10)
    ax.set_ylabel("Score", fontsize=11)
    ax.set_title(f"Model Comparison — {target}", fontsize=13)
    ax.set_ylim(0, 1.05)
    ax.legend()
    ax.bar_label(bars1, fmt="%.3f", padding=2, fontsize=8)
    ax.bar_label(bars2, fmt="%.3f", padding=2, fontsize=8)
    fig.tight_layout()

    path = os.path.join(OUTPUTS_DIR, f"{target}_model_comparison.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved bar chart: {path}")


# ── Training loop ─────────────────────────────────────────────────────────────────

def train_one_target(
    target: str,
    train_ohe: pd.DataFrame, train_cat: pd.DataFrame,
    val_ohe:   pd.DataFrame, val_cat:   pd.DataFrame,
    test_ohe:  pd.DataFrame, test_cat:  pd.DataFrame,
    train_raw: pd.DataFrame, test_raw:  pd.DataFrame,
    y_train: np.ndarray, y_val: np.ndarray, y_test: np.ndarray,
) -> Tuple[str, Any, Dict]:
    print(f"\n{'='*58}")
    print(f"Target: {target}  |  "
          f"Train+: {y_train.sum()}/{len(y_train)}  "
          f"Val+: {y_val.sum()}/{len(y_val)}  "
          f"Test+: {y_test.sum()}/{len(y_test)}")
    print("="*58)

    pos_w    = float((len(y_train) - y_train.sum()) / max(y_train.sum(), 1))
    cat_feats= [c for c in CATEGORICAL_FEATURES if c in train_cat.columns]

    all_models: Dict[str, Tuple[Any, pd.DataFrame, pd.DataFrame]] = {}

    # Standard models (train on OHE, calibrate on val_ohe)
    for name, mdl in _models(pos_w).items():
        mdl.fit(train_ohe, y_train)
        cal = CalibratedClassifierCV(mdl, method="isotonic", cv="prefit")
        cal.fit(val_ohe, y_val)
        all_models[name] = (cal, val_ohe, test_ohe)

    # CatBoost
    cat_mdl = _catboost(pos_w, cat_feats)
    cat_mdl.fit(train_cat, y_train, eval_set=(val_cat, y_val), early_stopping_rounds=30)
    all_models["CatBoost"] = (cat_mdl, val_cat, test_cat)

    results: Dict[str, Dict] = {}
    probs_for_curves: Dict[str, np.ndarray] = {}
    candidates = []

    for name, (mdl, _, X_te) in all_models.items():
        y_prob = mdl.predict_proba(X_te)[:, 1]
        m = _eval(y_test, y_prob)
        results[name] = m
        probs_for_curves[name] = y_prob

        flag = " <-- candidate" if m["recall"] >= MIN_RECALL else ""
        print(f"  [{name:20s}] PR-AUC={m['pr_auc']:.3f}  "
              f"Recall={m['recall']:.3f}  Prec={m['precision']:.3f}  "
              f"F1={m['f1']:.3f}  Brier={m['brier']:.4f}{flag}")

        if m["recall"] >= MIN_RECALL:
            candidates.append((name, m["pr_auc"], mdl))

    # Champion selection
    if candidates:
        candidates.sort(key=lambda x: x[1], reverse=True)
        best_name, _, best_model = candidates[0]
    else:
        print("  No model met recall floor — keeping LogisticRegression")
        best_name  = "LogisticRegression"
        best_model = all_models["LogisticRegression"][0]

    print(f"  --> Champion: {best_name}")

    # Save plots
    _save_pr_curves(probs_for_curves, y_test, target)
    _save_bar_comparison(results, target)
    _save_comparison_table(results, target)

    return best_name, best_model, results


# ── Artifact saving ───────────────────────────────────────────────────────────────

def save_model_artifacts(
    target: str,
    name: str,
    model: Any,
    metrics: Dict,
    prep: XAIPreprocessor,
    selections: Dict[str, str],
):
    os.makedirs(MODEL_STORE, exist_ok=True)

    with open(f"{MODEL_STORE}/{target}_model.pkl", "wb") as f:
        pickle.dump(model, f)

    with open(f"{MODEL_STORE}/{target}_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2, default=str)

    card = {
        "target": target,
        "champion_algorithm": name,
        "version": "1.0.0",
        "trained_at": datetime.utcnow().isoformat() + "Z",
        "feature_set_version": "xai_v1.0",
        "test_metrics": metrics.get(name, {}),
        "intended_use": "Early-warning risk detection; advisory only — human officer must verify.",
        "limitations": [
            "Trained on synthetic data; retrain with real MOSPI data before production use.",
            "CatBoost may underperform for sectors with < 30 training examples.",
        ],
        "human_in_loop": True,
    }
    with open(f"{MODEL_STORE}/{target}_model_card.json", "w") as f:
        json.dump(card, f, indent=2)

    print(f"  Saved: {target}_model.pkl, _metrics.json, _model_card.json")


def save_shared_artifacts(prep: XAIPreprocessor, selections: Dict[str, str]):
    with open(f"{MODEL_STORE}/scaler.pkl", "wb") as f:
        pickle.dump(prep.scaler, f)

    with open(f"{MODEL_STORE}/columns.json", "w") as f:
        json.dump({
            "ohe_cols":  prep.ohe_cols,
            "cat_cols":  prep.cat_cols,
            "numeric":   NUMERIC_FEATURES,
            "categorical": CATEGORICAL_FEATURES,
            "feature_set_version": "xai_v1.0",
        }, f, indent=2)

    with open(f"{MODEL_STORE}/selections.json", "w") as f:
        json.dump(selections, f, indent=2)

    print(f"Shared artifacts saved -> {MODEL_STORE}")


# ── Main ──────────────────────────────────────────────────────────────────────────

def main():
    # 1. Load / generate data
    if not os.path.exists(DATASET_CSV):
        print("Generating synthetic dataset ...")
        from backend.ml_core.data.generator import generate_synthetic_data
        df = generate_synthetic_data()
        df.to_csv(DATASET_CSV, index=False)
    else:
        df = pd.read_csv(DATASET_CSV)
    print(f"Loaded {len(df):,} rows, {df['project_id'].nunique():,} projects")

    # 2. Build features
    cache = os.path.join(PROCESSED, "xai_features.parquet")
    if os.path.exists(cache):
        print("Loading cached features ...")
        feat_df = pd.read_parquet(cache)
    else:
        print("Building features ...")
        feat_df = build_training_dataset(
            df, TRAIN_CUTOFFS + VAL_CUTOFFS + TEST_CUTOFFS, verbose=True
        )
        feat_df.to_parquet(cache, index=False)

    print(f"\nFeature rows: {len(feat_df):,}")
    for t in TARGETS:
        rate = feat_df[t].mean() * 100
        print(f"  {t}: {rate:.1f}% positive")

    # 3. Split
    train_df = feat_df[feat_df["as_of_date"].isin(TRAIN_CUTOFFS)]
    val_df   = feat_df[feat_df["as_of_date"].isin(VAL_CUTOFFS)]
    test_df  = feat_df[feat_df["as_of_date"].isin(TEST_CUTOFFS)]
    print(f"\nSplit: Train={len(train_df)}, Val={len(val_df)}, Test={len(test_df)}")

    drop = TARGETS + ["project_id", "as_of_date"]

    # 4. Preprocess
    prep = XAIPreprocessor()
    train_ohe, train_cat = prep.fit_transform(train_df, drop)
    val_ohe,   val_cat   = prep.transform(val_df,   drop)
    test_ohe,  test_cat  = prep.transform(test_df,  drop)

    # 5. Train
    selections: Dict[str, str] = {}
    for target in TARGETS:
        y_tr = train_df[target].values.astype(int)
        y_va = val_df[target].values.astype(int)
        y_te = test_df[target].values.astype(int)

        name, model, metrics = train_one_target(
            target,
            train_ohe, train_cat,
            val_ohe,   val_cat,
            test_ohe,  test_cat,
            train_df,  test_df,
            y_tr, y_va, y_te,
        )
        save_model_artifacts(target, name, model, metrics, prep, selections)
        selections[target] = name

    save_shared_artifacts(prep, selections)

    print("\n[DONE] XAI training complete.")
    for t, n in selections.items():
        print(f"  {t}: {n}")


if __name__ == "__main__":
    main()
