"""
PRAGYA XAI — generate_examples.py
Produces 3 concrete example explained predictions on real projects
from dataset.csv, saves charts to outputs/ and prints a report.

Run AFTER training:
    $env:PYTHONPATH="."; python backend/pragya_xai/generate_examples.py
"""
from __future__ import annotations

import json
import os
import sys

import pandas as pd

from backend.pragya_xai.explain.shap_explainer import explain_risk, plot_global_shap
from backend.pragya_xai.explain.shap_explainer import _REGISTRY

ROOT        = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATASET_CSV = os.path.join(ROOT, "dataset.csv")
OUTPUTS_DIR = os.path.join(ROOT, "backend", "pragya_xai", "outputs")
MODEL_STORE = os.path.join(ROOT, "backend", "pragya_xai", "model_store")

os.makedirs(OUTPUTS_DIR, exist_ok=True)


def pick_projects(df: pd.DataFrame) -> list[tuple[str, str, str]]:
    """
    Pick 3 representative projects:
        1. Overrun project  — label_overrun=1
        2. Delayed project  — delayed_flag=1, overrun_flag=0
        3. Healthy project  — both flags 0
    Returns list of (project_id, as_of_date, description).
    """
    # Latest update per project
    df["update_date"] = pd.to_datetime(df["update_date"])
    latest = df.sort_values("update_date").groupby("project_id").last().reset_index()

    overrun = latest[latest["overrun_flag"] == 1]
    delayed = latest[(latest["delayed_flag"] == 1) & (latest["overrun_flag"] == 0)]
    healthy = latest[(latest["delayed_flag"] == 0) & (latest["overrun_flag"] == 0)]

    picks = []
    for subset, desc in [
        (overrun, "High-Risk (Cost Overrun)"),
        (delayed, "Medium-Risk (Time Delay only)"),
        (healthy, "Low-Risk (On Track)"),
    ]:
        if subset.empty:
            continue
        row    = subset.sample(1, random_state=42).iloc[0]
        pid    = row["project_id"]
        as_of  = row["update_date"].strftime("%Y-%m-%d")
        picks.append((pid, as_of, desc))

    return picks[:3]


def run_examples():
    if not os.path.exists(DATASET_CSV):
        print(f"[ERROR] {DATASET_CSV} not found. Run data generator first.")
        sys.exit(1)

    df = pd.read_csv(DATASET_CSV)
    print(f"Loaded {len(df):,} rows from dataset.csv\n")

    picks = pick_projects(df)
    if not picks:
        print("[ERROR] Could not find representative projects.")
        sys.exit(1)

    # Also load test split features for global chart
    feat_cache = os.path.join(ROOT, "backend", "pragya_xai", "outputs", "processed", "xai_features.parquet")

    all_results = []

    for i, (pid, as_of, desc) in enumerate(picks, 1):
        print(f"{'='*60}")
        print(f"Example {i}: {desc}")
        print(f"  Project ID : {pid}")
        print(f"  As-of Date : {as_of}")

        proj_df = df[df["project_id"] == pid].copy()

        for target in ("label_overrun", "label_delay"):
            result = explain_risk(
                project_id=pid,
                as_of_date=as_of,
                project_updates_df=proj_df,
                target=target,
                top_k=5,
                save_chart=True,
            )

            if "error" in result:
                print(f"  [{target}] Error: {result['error']}")
                continue

            print(f"\n  Target: {target.replace('label_', '').upper()}")
            print(f"  Risk Score : {result['risk_probability']:.1%}  [{result['risk_band']}]")
            print(f"  Top Reasons:")
            for j, reason in enumerate(result["top_reasons"], 1):
                print(f"    {j}. {reason}")
            if result.get("chart_path"):
                print(f"  Chart saved: {result['chart_path']}")

            # Strip base64 from saved JSON (too large)
            save = {k: v for k, v in result.items() if k != "shap_chart"}
            all_results.append(save)

        print()

    # Save all example results as JSON
    out_json = os.path.join(OUTPUTS_DIR, "example_predictions.json")
    with open(out_json, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"Example results saved: {out_json}")

    # ── Global SHAP chart ─────────────────────────────────────────────────────
    _REGISTRY.load()
    if os.path.exists(feat_cache) and _REGISTRY.models:
        try:
            feat_df = pd.read_parquet(feat_cache)
            test_df = feat_df[feat_df["as_of_date"] == "2023-01-01"]
            if not test_df.empty:
                drop = ["label_overrun", "label_delay", "project_id", "as_of_date", "label_impl_risk"]
                model = _REGISTRY.models.get("label_overrun")
                if model:
                    _, X_cat = _REGISTRY.preprocess(
                        test_df.drop(columns=[c for c in drop if c in test_df.columns]).iloc[0].to_dict()
                    )
                    # Build full X for sample
                    rows = []
                    for _, row in test_df.head(300).iterrows():
                        row_d = {k: v for k, v in row.to_dict().items() if k not in drop}
                        _, xc = _REGISTRY.preprocess(row_d)
                        rows.append(xc)
                    X_sample = pd.concat(rows, ignore_index=True)

                    gpath = os.path.join(OUTPUTS_DIR, "global_shap_overrun.png")
                    plot_global_shap(model, X_sample, "label_overrun", save_path=gpath)
                    print(f"Global SHAP chart saved: {gpath}")
        except Exception as exc:
            print(f"[WARN] Global chart skipped: {exc}")

    print("\n[DONE] All example outputs generated.")


if __name__ == "__main__":
    run_examples()
