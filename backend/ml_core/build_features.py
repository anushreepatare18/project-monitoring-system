"""
PRAGYA AI — End-to-End Feature Build & Dataset Preparation

Orchestrates:
  1. Load dataset.csv (generate if missing)
  2. Build point-in-time features across rolling cutoffs
  3. Save train / val / test splits
  4. Print summary stats

Run from project root:
    $env:PYTHONPATH="."; python backend/ml_core/build_features.py
"""

from __future__ import annotations

import os
import sys
import time

import pandas as pd

from backend.ml_core.features.pipeline import (
    build_training_dataset,
    temporal_split,
)

DATASET_CSV   = "dataset.csv"
PROCESSED_DIR = "backend/ml_core/data/processed"

TRAIN_CUTOFFS = ["2019-01-01", "2020-01-01", "2021-01-01"]
VAL_CUTOFFS   = ["2022-01-01"]
TEST_CUTOFFS  = ["2023-01-01"]
ALL_CUTOFFS   = TRAIN_CUTOFFS + VAL_CUTOFFS + TEST_CUTOFFS


def main():
    # ── 1. Load / generate data ───────────────────────────────────────────────
    if not os.path.exists(DATASET_CSV):
        print(f"[INFO] {DATASET_CSV} not found. Generating synthetic dataset...")
        from backend.ml_core.data.generator import generate_synthetic_data
        df = generate_synthetic_data()
        df.to_csv(DATASET_CSV, index=False)
        print(f"[INFO] Generated and saved {len(df):,} rows.")
    else:
        df = pd.read_csv(DATASET_CSV)
        print(f"[INFO] Loaded {len(df):,} rows from {DATASET_CSV}")
        print(f"       Projects: {df['project_id'].nunique():,}")

    # ── 2. Build features ─────────────────────────────────────────────────────
    print("\n[INFO] Building point-in-time features...")
    t0 = time.time()
    features_df = build_training_dataset(df, ALL_CUTOFFS, verbose=True)
    elapsed = time.time() - t0
    print(f"[INFO] Feature build complete in {elapsed:.1f}s")
    print(f"[INFO] Total feature rows: {len(features_df):,}")

    if features_df.empty:
        print("[ERROR] No features were built. Check your dataset columns and cutoff dates.")
        sys.exit(1)

    # ── 3. Label distribution ─────────────────────────────────────────────────
    print("\nLabel distributions:")
    for lbl in ["label_overrun", "label_delay", "label_impl_risk"]:
        if lbl in features_df.columns:
            rate = features_df[lbl].mean() * 100
            print(f"  {lbl}: {rate:.1f}% positive")

    # ── 4. Temporal split ─────────────────────────────────────────────────────
    train, val, test = temporal_split(features_df, TRAIN_CUTOFFS, VAL_CUTOFFS, TEST_CUTOFFS)
    print(f"\nSplits: Train={len(train):,}  Val={len(val):,}  Test={len(test):,}")

    os.makedirs(PROCESSED_DIR, exist_ok=True)
    train.to_csv(f"{PROCESSED_DIR}/train.csv", index=False)
    val.to_csv(f"{PROCESSED_DIR}/val.csv",     index=False)
    test.to_csv(f"{PROCESSED_DIR}/test.csv",   index=False)

    # Also save feature cache as parquet for fast reloads
    features_df.to_parquet(f"{PROCESSED_DIR}/all_features.parquet", index=False)

    print(f"\n[INFO] Saved train/val/test splits and feature cache to {PROCESSED_DIR}/")
    print("[DONE] build_features.py complete.")


if __name__ == "__main__":
    main()
