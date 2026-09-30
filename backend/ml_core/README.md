# PRAGYA AI — ML + XAI Core

> Predictive Intelligence Layer for the Government Project Monitoring System  
> Team CivicMind · SIH26103

---

## Architecture Overview

```
dataset.csv
    │
    ▼
backend/ml_core/
├── data/
│   ├── generator.py          # Synthetic 2000-project dataset generator
│   └── processed/            # train.csv, val.csv, test.csv, all_features.parquet
│
├── features/
│   └── pipeline.py           # Shared feature computation (train ≡ serve)
│                               compute_features(df, as_of_date) → dict
│                               compute_labels(df, as_of_date, sector) → dict
│                               build_training_dataset(df, cutoffs) → DataFrame
│
├── training/
│   └── train.py              # Full training + evaluation + artifact saving
│
├── explain/
│   └── explainer.py          # SHAP + plain-language translator
│
├── anomaly/
│   └── detector.py           # Isolation Forest + rule-based checks
│
├── inference/
│   └── infer.py              # PragyaInferenceEngine + run_inference() API contract
│
├── registry/                 # Saved model artifacts (auto-created by training)
│   ├── label_overrun_model.pkl
│   ├── label_delay_model.pkl
│   ├── label_impl_risk_model.pkl
│   ├── scaler.pkl
│   ├── columns.json
│   ├── anomaly_detector.pkl
│   ├── model_card.json
│   └── *_metrics.json
│
├── tests/
│   └── test_pipeline.py      # pytest: leakage, features, labels, splits, anomaly
│
└── build_features.py         # Feature-build orchestrator
```

---

## Setup

```bash
# From project root (SIH26103/)
pip install scikit-learn xgboost catboost shap pandas numpy pyarrow pytest
```

---

## Running End-to-End Training

```bash
# Step 1 — Generate synthetic dataset (skip if you have dataset.csv)
$env:PYTHONPATH="."; python backend/ml_core/data/generator.py

# Step 2 — Build features and temporal splits
$env:PYTHONPATH="."; python backend/ml_core/build_features.py

# Step 3 — Train all models, evaluate, save artifacts
$env:PYTHONPATH="."; python backend/ml_core/training/train.py

# Step 4 — Run tests
$env:PYTHONPATH="."; pytest backend/ml_core/tests/ -v
```

All steps are idempotent. Step 2 caches features in `all_features.parquet` — subsequent
training runs reuse the cache automatically.

---

## Calling Inference

```python
from backend.ml_core.inference.infer import run_inference
import pandas as pd

# Load project history (any number of update rows for ONE project)
df = pd.read_csv("dataset.csv")
project_df = df[df["project_id"] == "PRJ-ABCD1234"]

result = run_inference(
    project_id="PRJ-ABCD1234",
    as_of_date="2023-06-01",
    project_updates_df=project_df,
)

print(result)
# {
#   "p_cost": 0.7823,          # P(cost overrun)
#   "p_time": 0.6412,          # P(time delay)
#   "p_impl": 0.5930,          # P(implementation risk)
#   "composite_risk_score": 0.6994,
#   "risk_band": "High",
#   "shap_explanation": [
#     {"feature": "progress_gap", "value": 22.4, "impact": 0.18,
#      "explanation": "Progress is 22.4 points behind the expected schedule level..."},
#     ...
#   ],
#   "anomaly_score": 0.12,
#   "anomaly_triggers": [],
#   "model_version": "2.0.0",
#   "feature_set_version": "v2.0"
# }
```

---

## Feature Engineering

All 20+ features are computed by `compute_features(project_df, as_of_date)`:

| Feature | Description |
|---|---|
| `progress_gap` | Expected progress − actual progress |
| `velocity_last_1/3/6` | Progress %/day over last 1, 3, 6 updates |
| `velocity_needed_to_finish` | Required pace to meet planned deadline |
| `pct_milestones_delayed` | Fraction of milestones that are late |
| `max_milestone_delay_months` | Worst milestone delay in months |
| `cost_growth_pct` | (Revised cost − Sanctioned) / Sanctioned × 100 |
| `expenditure_to_progress_ratio` | Burn rate vs physical achievement |
| `burn_rate_per_day` | Daily cost spend over last 4 updates |
| `days_since_last_update` | Monitoring cadence gap |
| `avg_update_gap` | Average days between historical updates |
| `count_of_revised_dates` | Number of expected-completion-date revisions |
| `project_age_days` | Days elapsed since planned start |
| `planned_duration_days` | Total planned project duration |
| `n_updates_so_far` | Count of updates before as_of_date |
| `sector`, `ministry`, `agency` | Categoricals (native for CatBoost, OHE for LR/RF/XGB) |
| `*_missing` flags | Missingness indicators for imputed fields |

**Leakage guarantee**: `compute_features` raises `ValueError` immediately if any
row's `update_date` is after `as_of_date`.

---

## Models

| Target | Models Trained | Selection Criterion |
|---|---|---|
| `label_overrun` | LR, RF, XGBoost, CatBoost | Best PR-AUC with Recall ≥ 0.50 |
| `label_delay` | LR, RF, XGBoost, CatBoost | Best PR-AUC with Recall ≥ 0.50 |
| `label_impl_risk` | LR, RF, XGBoost, CatBoost | Best PR-AUC with Recall ≥ 0.50 |

Probabilities are calibrated on the validation fold (isotonic regression).

---

## Labels

| Label | Definition |
|---|---|
| `label_overrun` | `final_cost > sanctioned_cost × (1 + sector_tolerance)` |
| `label_delay` | `final_end_date > planned_end + max(90 days, 10% of planned duration)` |
| `label_impl_risk` | Progress gain < 3% in 6-month forward window, OR delay/overrun |

Sector tolerances: Highways 15%, Railways 12%, all others 10%.

---

## Temporal Splits

| Split | Cutoff Dates |
|---|---|
| Train | 2019-01-01, 2020-01-01, 2021-01-01 |
| Validation | 2022-01-01 |
| Test | 2023-01-01 |

No project is shared across train and test for the same horizon.

---

## Anomaly Detection

Two-stage pipeline:

1. **Rule-based** (fast, always runs):
   - Progress > 100% or < 0%
   - Expenditure > 2.5× sanctioned
   - Revised cost > 3× sanctioned
   - Progress jump > 30% in one update
   - No update for > 180 days
   - Expected completion date passed with < 95% progress

2. **Isolation Forest** (unsupervised ML on update-to-update deltas):
   - Features: `prog_velocity`, `exp_velocity`, `date_shift_days`, `rev_cost_jump_pct`
   - Trained once on full dataset; produces a continuous anomaly score

Combined score = `max(rule_score, ml_score × 0.7)`.

---

## Important Constraints

- **Human-in-the-loop**: The model NEVER takes automated action. All predictions are
  advisory and must be verified by a monitoring officer before any intervention.
- **Calibration**: All probabilities are calibrated via isotonic regression on the
  held-out validation fold.
- **Reproducibility**: All random seeds fixed at 42. Library versions are pinned in
  `requirements.txt`.
