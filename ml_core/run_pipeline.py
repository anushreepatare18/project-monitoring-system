"""
PRAGYA AI — End-to-End Pipeline Runner  (v2)
=============================================
Run this script to:
  1. Generate synthetic training data
  2. Train the Isolation Forest anomaly detector
  3. Train & evaluate all three risk models (overrun, delay, impl_risk)
  4. Generate global SHAP charts for each model
  5. Print a summary report with 3 example explained predictions

Usage (from repo root):
    python -m ml_core.run_pipeline
"""
from __future__ import annotations

import pickle
import sys
import os
from pathlib import Path

# Ensure the repo root is on the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd

TARGETS = ["overrun_flag", "delayed_flag", "implementation_risk_flag"]
DATA_PATH = "ml_core/data/synthetic_projects.csv"


def run_all() -> None:
    print("\n" + "=" * 65)
    print("  PRAGYA AI — Full Training Pipeline")
    print("=" * 65)

    # -- 1. Generate Data ------------------------------------------------------
    print("\n[1/5] Generating synthetic training data …")
    from ml_core.data.generator import generate_synthetic_data
    df = generate_synthetic_data(output_file=DATA_PATH)
    print(f"      [OK] {len(df):,} updates across {df['project_id'].nunique():,} projects")

    # -- 2. Train Anomaly Detector ---------------------------------------------
    print("\n[2/5] Training Isolation Forest anomaly detector …")
    from ml_core.anomaly.detector import train_anomaly_detector
    train_anomaly_detector(data_path=DATA_PATH)

    # -- 3. Train Risk Models --------------------------------------------------
    print("\n[3/5] Training risk models for all targets …")
    from ml_core.training.train import train_and_evaluate
    all_results: dict[str, dict] = {}
    for target in TARGETS:
        results = train_and_evaluate(target, data_path=DATA_PATH)
        all_results[target] = results

    # -- 4. Global SHAP Charts -------------------------------------------------
    print("\n[4/5] Generating global SHAP importance charts …")
    from ml_core.explain.shap_explainer import explain_global
    from ml_core.features.pipeline import compute_features
    df_full = pd.read_csv(DATA_PATH)

    for target in TARGETS:
        model_path = f"ml_core/registry/{target}_best_model.pkl"
        if not os.path.exists(model_path):
            print(f"      [!] Model not found for {target}, skipping SHAP global.")
            continue
        with open(model_path, "rb") as fh:
            payload = pickle.load(fh)
        model = payload["model"]
        model_name = payload.get("model_name", "unknown")

        # Use a sample of training data for background
        sample_df = df_full.sample(min(300, len(df_full)), random_state=42)
        try:
            X_bg = compute_features(sample_df, "2040-01-01").reset_index(drop=True)
            chart_path = explain_global(model, X_bg, model_name, target, n_samples=200)
            if chart_path:
                print(f"      [OK] Global SHAP chart -> {chart_path}")
        except Exception as e:
            print(f"      [!] SHAP global chart for {target} failed: {e}")

    # -- 5. Example Explained Predictions -------------------------------------
    print("\n[5/5] Generating 3 example explained predictions …")
    from ml_core.inference.predict import predict_project

    df_full["update_date"] = pd.to_datetime(df_full["update_date"])
    sample_pids = df_full["project_id"].sample(3, random_state=7).tolist()

    for pid in sample_pids:
        pid_df   = df_full[df_full["project_id"] == pid]
        as_of    = str(pid_df["update_date"].max().date())
        try:
            result = predict_project(pid, as_of, df_full)
            print(f"\n  -- Project: {pid} (as of {as_of}) --")
            print(f"     Risk Band  : {result['risk_band']}")
            print(f"     p_cost     : {result['p_cost']:.3f}")
            print(f"     p_time     : {result['p_time']:.3f}")
            print(f"     p_impl     : {result['p_impl']:.3f}")
            print(f"     Composite  : {result['composite_risk_score']:.3f}")
            print(f"     Anomaly    : {result['anomaly_score']:.3f}")
            print("     Top reasons:")
            for ex in result["shap_explanation"][:3]:
                print(f"       -> {ex['text']}")
        except Exception as e:
            print(f"     [!] Could not score {pid}: {e}")

    # -- Summary ---------------------------------------------------------------
    print("\n" + "=" * 65)
    print("  Pipeline Complete!")
    print("  Models saved in:  ml_core/registry/")
    print("  Charts saved in:  ml_core/registry/*.png")
    print("=" * 65)


if __name__ == "__main__":
    run_all()
