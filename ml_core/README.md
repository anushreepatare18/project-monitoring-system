# PRAGYA AI — ML + XAI Core

Predictive intelligence layer for the Government Project Monitoring System (SIH26103, Team CivicMind).

> ⚠️ **Human-in-the-loop always.** Models surface early warnings; government officers verify before acting. No automated action is taken based on model output.

---

## Directory Layout

```
ml_core/
├── data/         generator.py          — synthetic dataset (2,000 projects × 5–12 updates)
├── features/     pipeline.py           — shared feature function (train = inference)
├── training/     train.py              — LR / RF / XGB / CatBoost + rolling-origin backtest
├── explain/      shap_explainer.py     — SHAP + plain-language translator
├── anomaly/      detector.py           — Isolation Forest + rule-based checks
├── inference/    predict.py            — single callable contract for backend/chatbot
├── registry/     *.pkl, *.json, *.png  — saved models, metrics, charts
├── tests/        test_leakage.py       — pytest (10 cases: leakage, pipeline, features)
└── run_pipeline.py                     — end-to-end runner
```

---

## How to Run End-to-End

### 1. Install dependencies

```bash
pip install -r ml_core/requirements.txt
```

### 2. Run the full pipeline (from repo root)

```bash
python -m ml_core.run_pipeline
```

This will:
1. Generate `ml_core/data/synthetic_projects.csv` (~2,000 projects, ~14,000 rows)
2. Train the Isolation Forest anomaly detector
3. Train and evaluate **3 targets** (cost overrun, time delay, implementation risk):
   - Logistic Regression (baseline), Random Forest, XGBoost, CatBoost
   - Isotonic probability calibration on validation fold
   - Rolling-origin backtest (3 cutoffs)
4. Select the best model per target (highest val PR-AUC ≥ recall floor 0.45)
5. Save models, metrics JSON, model cards, and calibration/PR-curve plots to `ml_core/registry/`
6. Generate global SHAP importance charts
7. Print 3 example explained predictions

### 3. Run tests

```bash
pytest ml_core/tests/ -v
```

---

## Calling Inference

```python
from ml_core.inference.predict import predict_project, explain_risk
import pandas as pd

df = pd.read_csv("ml_core/data/synthetic_projects.csv")

# Full inference contract
result = predict_project("PRJ-123456", "2026-10-01", df)
# Returns:
# {
#   "p_cost":               0.76,   # cost-overrun probability
#   "p_time":               0.45,   # time-delay probability
#   "p_impl":               0.12,   # implementation-risk probability
#   "composite_risk_score": 0.49,
#   "risk_band":            "High",
#   "shap_explanation":     [ { "feature": "...", "shap_value": 0.23, "text": "..." } ],
#   "shap_chart":           "ml_core/registry/shap_PRJ-123456_overrun_flag.png",
#   "anomaly_score":        -0.12,
#   "anomaly_reasons":      "Sudden expenditure spike...",
#   "model_version":        "v2.0.0",
#   "feature_set_version":  "v2",
#   "as_of_date":           "2026-10-01",
# }

# Dashboard/chatbot contract
expl = explain_risk("PRJ-123456", "2026-10-01", df)
# Returns:
# {
#   "risk_probability":    0.76,
#   "risk_band":           "High",
#   "top_reasons":         ["Progress is 20% below expected...", ...],
#   "shap_chart":          "...",
#   "model_version":       "v2.0.0",
#   "feature_set_version": "v2",
#   "as_of_date":          "2026-10-01",
# }
```

---

## Feature Engineering

**One function, used identically for training and inference:**

```python
from ml_core.features.pipeline import compute_features
X = compute_features(df_history, as_of_date="2026-10-01")
```

### Features computed

| Feature | Description |
|---|---|
| `progress_gap` | Expected progress (linear plan) − actual physical progress |
| `progress_velocity_1` | Progress delta since last update |
| `progress_velocity_3` | Mean progress per update over last 3 updates |
| `velocity_needed_to_finish` | Required daily progress rate to meet deadline |
| `max_milestone_delay_months` | Longest milestone slip (actual or expected) in months |
| `pct_milestones_delayed` | Fraction of milestones currently delayed |
| `cost_growth_pct` | (revised_cost − sanctioned_cost) / sanctioned_cost × 100 |
| `expenditure_to_progress_ratio` | Actual spend vs. expected spend for progress achieved |
| `burn_rate` | Cumulative spend vs. expected spend for time elapsed |
| `days_since_last_update` | Reporting gap |
| `avg_update_gap` | Running mean of update gaps |
| `count_of_revised_dates` | Number of times expected completion was revised past planned end |
| `missing_velocity_flag` | 1 if this is the first update (no predecessor to diff) |
| `sector / ministry / agency / state / project_type` | Categorical (native for CatBoost; OHE for others) |

### Leakage check

```python
# Raises AssertionError immediately if any row has update_date > as_of_date:
# AssertionError: LEAKAGE DETECTED: 3 rows have update_date after as_of_date 2026-03-01.
compute_features(df, as_of_date="2026-03-01")
```

---

## Labels

| Label | Definition | Default tolerance |
|---|---|---|
| `overrun_flag` | `final_cost > sanctioned_cost × (1 + tol)` | 10% (Roads: 12%, Railways: 15%) |
| `delayed_flag` | `final_end_date > planned_end + max(90d, 10% of planned duration)` | — |
| `implementation_risk_flag` | Stagnation OR delay ratio > 25% above 1.25× planned duration | — |

**Train/test split is strictly temporal** — projects are ordered by `outcome_known_at`, and no project appears in both train and test for the same prediction horizon.

---

## Model Evaluation (primary metric: PR-AUC)

> PR-AUC is preferred over ROC-AUC because labels are highly imbalanced (~25-30% positive rate).

Metrics reported per model, on the held-out test period:
- PR-AUC (primary), ROC-AUC, Brier Score (calibration)
- Precision, Recall, F1 at operating threshold 0.40
- Per-sector slices
- Rolling-origin backtest (3 cutoffs)

Model selection rule: **highest val PR-AUC subject to recall ≥ 0.45**. If no model clears the floor, LogisticRegression baseline is kept.

---

## Reproducibility

- All random seeds fixed: `RANDOM_SEED = 42`
- Library versions pinned in `ml_core/requirements.txt`
- Dataset generated deterministically from `random_seed=42`
- Re-running `python -m ml_core.run_pipeline` produces identical models

---

## Model Cards

Each saved model has a JSON model card at `ml_core/registry/{target}_model_card.json` containing:
- intended use, limitations, known weak sectors
- training and test date ranges
- test-period metrics

---

## Chatbot Integration

The chatbot calls `explain_risk()` via the results store. It **never re-runs inference** on the fly for question-answering; it reads from the pre-computed results table. See `chatbot/README.md` for the grounding architecture.
