# PRAGYA AI - Predictive Intelligence Layer

This directory (`ml_core`) contains the end-to-end Machine Learning and Explainable AI (XAI) pipeline for PRAGYA AI.

## Directory Structure
- `data/`: Contains `generator.py` to create the simulated project timeline dataset (`synthetic_projects.csv`).
- `features/`: Contains `pipeline.py` which engineers features strictly bound by an `as_of_date` to prevent future leakage.
- `training/`: Contains `train.py` for time-series split training, model comparison (LR, RF, XGB, CatBoost), isotonic calibration, and evaluation.
- `explain/`: Contains `shap_explainer.py` to generate top-5 SHAP feature contributions and translate them into officer-friendly plain language.
- `anomaly/`: Contains `detector.py` implementing an Isolation Forest to flag unusual update-to-update deltas (e.g., implausible physical progress drops).
- `inference/`: Contains `predict.py` with the single callable API contract `predict_project(project_id, as_of_date, df_history)`.
- `registry/`: Artifact store for saved `*.pkl` models and metrics reports.
- `tests/`: Contains pytest assertions for leakage constraints.

## How to Run End-to-End

1. Ensure requirements are installed:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the full pipeline from the root directory:
   ```bash
   python -m ml_core.run_pipeline
   ```
   This will:
   - Generate synthetic training data.
   - Train the Anomaly Detector.
   - Train and evaluate the Risk Models (Cost Overrun and Delay), selecting the best performer based on PR-AUC.
   - Save models to `ml_core/registry/`.

3. Run tests:
   ```bash
   pytest ml_core/tests/
   ```

## Calling Inference

From your backend (e.g., FastAPI), use the unified contract:

```python
from ml_core.inference.predict import predict_project
import pandas as pd

history_df = pd.read_csv("path/to/data.csv")
result = predict_project("PRJ-123456", "2026-10-01", history_df)
print(result)
```

**Returns:**
```json
{
  "p_cost": 0.76,
  "p_time": 0.45,
  "p_impl": 0.0,
  "composite_risk_score": 0.48,
  "risk_band": "High",
  "shap_explanation": [
     {"feature": "progress_gap", "shap_value": 0.23, "text": "Progress is 15% below the expected level, which increases risk."}
  ],
  "anomaly_score": -0.12,
  "anomaly_reasons": "Financial progress significantly outpaces physical."
}
```
