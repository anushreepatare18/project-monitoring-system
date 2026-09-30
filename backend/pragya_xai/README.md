# PRAGYA XAI — Explainable AI Risk Prediction Module

> Government Project Monitoring System · Team CivicMind · SIH26103

---

## What This Is

PRAGYA XAI predicts **delay** and **cost overrun** risk for Central Sector
infrastructure projects and explains every prediction in plain English using
SHAP — so a non-technical monitoring officer can understand *why* a project
is flagged.

```
dataset.csv
    │
    ▼
/features/pipeline.py      compute_features(project_df, as_of_date) — train & serve
    │
    ▼
/training/train.py         4 models × 2 targets, calibrated, evaluated
    │
    ▼
/model_store/              saved model PKLs + model cards + scaler + columns
    │
    ▼
/explain/shap_explainer.py explain_risk(project_id, as_of_date, df) → result dict
    │
    ▼
/outputs/                  PR curves, bar charts, SHAP charts, example JSON
```

---

## Setup

```bash
pip install scikit-learn xgboost catboost shap pandas numpy matplotlib seaborn pyarrow
```

---

## End-to-End Run

```powershell
# From project root (SIH26103/)

# Step 1 — Generate data (skip if dataset.csv exists)
$env:PYTHONPATH="."; python backend/ml_core/data/generator.py

# Step 2 — Train models (builds feature cache automatically)
$env:PYTHONPATH="."; python backend/pragya_xai/training/train.py

# Step 3 — Run tests (22 tests, no models needed)
$env:PYTHONPATH="."; pytest backend/pragya_xai/tests/ -v

# Step 4 — Generate 3 example explained predictions
$env:PYTHONPATH="."; python backend/pragya_xai/generate_examples.py
```

---

## Calling `explain_risk()`

```python
from backend.pragya_xai.explain.shap_explainer import explain_risk
import pandas as pd

df    = pd.read_csv("dataset.csv")
proj  = df[df["project_id"] == "PRJ-ABCD1234"]

result = explain_risk(
    project_id        = "PRJ-ABCD1234",
    as_of_date        = "2022-06-01",
    project_updates_df= proj,
    target            = "label_overrun",   # or "label_delay"
    top_k             = 5,
    save_chart        = True,              # saves PNG to outputs/
)

print(result["risk_band"])           # "High" | "Medium" | "Low"
print(result["risk_probability"])    # 0.83
print(result["top_reasons"])         # ["Progress is 22 pts behind...", ...]
# result["shap_chart"]  is a base64 PNG — embed with <img src="data:image/png;base64,{v}">
# result["chart_path"]  is the absolute path to the saved PNG
```

**Return contract** (stable — backend/dashboard calls this):

| Key | Type | Description |
|---|---|---|
| `project_id` | str | Echo of input |
| `as_of_date` | str | Echo of input |
| `target` | str | 'label_overrun' or 'label_delay' |
| `risk_probability` | float [0,1] | Calibrated probability |
| `risk_band` | str | 'High' / 'Medium' / 'Low' |
| `top_reasons` | list[str] | Plain-English sentences (top 5 SHAP features) |
| `shap_contributions` | list[dict] | {feature, value, impact, explanation} |
| `shap_chart` | str | Base64-encoded PNG bar chart |
| `chart_path` | str|None | Path to saved PNG |
| `model_version` | str | e.g. "1.0.0" |
| `feature_set_version` | str | e.g. "xai_v1.0" |

---

## Features (16 numeric + 3 categorical)

| Feature | Meaning |
|---|---|
| `progress_gap` | Expected % − Actual % progress |
| `velocity_last_1/3/6` | Progress %/day over last 1, 3, 6 updates |
| `velocity_needed_to_finish` | Required pace to meet deadline |
| `pct_milestones_delayed` | Fraction of milestones late |
| `max_milestone_delay_months` | Worst milestone delay (months) |
| `cost_growth_pct` | (Revised − Sanctioned) / Sanctioned × 100 |
| `expenditure_to_progress_ratio` | Burn rate vs physical progress |
| `burn_rate_per_day` | Daily spend over last 4 updates |
| `days_since_last_update` | Monitoring gap |
| `avg_update_gap` | Average days between historical updates |
| `count_of_revised_dates` | Number of completion-date revisions |
| `project_age_days` | Days elapsed since planned start |
| `planned_duration_days` | Total planned project duration |
| `n_updates_so_far` | Count of updates before as_of |
| `sector`, `ministry`, `agency` | Categoricals |

**Leakage guarantee**: `compute_features` raises `ValueError` immediately if any row's
`update_date` is after `as_of_date`. Tested by 4 dedicated pytest cases.

---

## Labels

| Label | Definition |
|---|---|
| `label_overrun` | `final_cost > sanctioned × (1 + sector_tol)` |
| `label_delay` | `final_end > planned_end + max(90 days, 10% of duration)` |

Sector tolerances: Highways 15%, Railways 12%, all others 10%.

---

## Models & Selection

| Model | Notes |
|---|---|
| LogisticRegression | Baseline, class_weight='balanced' |
| RandomForest | 200 trees, balanced, max_depth=10 |
| XGBoost | scale_pos_weight, 200 estimators |
| CatBoost | Native categoricals, 300 iters, early stopping |

**Selection rule**: Best PR-AUC on held-out test set, subject to Recall >= 0.50.
Fallback to Logistic Regression if no advanced model qualifies.

Probabilities are calibrated via **isotonic regression** on the validation fold.

---

## Temporal Splits

| Split | Cutoff Dates |
|---|---|
| Train | 2019-01-01, 2020-01-01, 2021-01-01 |
| Validation | 2022-01-01 |
| Test | 2023-01-01 |

No project is shared across train and test for the same prediction horizon.

---

## Outputs

After running the full pipeline, `backend/pragya_xai/outputs/` will contain:

```
label_overrun_pr_curves.png       PR curve for all 4 models
label_overrun_model_comparison.png Bar chart: PR-AUC & Recall per model
label_delay_pr_curves.png
label_delay_model_comparison.png
label_overrun_comparison.csv      Full metric table
label_delay_comparison.csv
{project_id}_{target}_{date}.png  Per-project SHAP bar charts
global_shap_overrun.png           Global feature importance
example_predictions.json          3 example explained predictions
```

---

## Human-in-the-Loop

> **The model never takes automated action.**  
> All predictions are advisory. Every alert must be reviewed and verified
> by a qualified monitoring officer before any intervention.
