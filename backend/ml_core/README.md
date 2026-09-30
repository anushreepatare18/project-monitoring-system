# PRAGYA AI - ML Core
This is the machine learning core for PRAGYA AI, predicting project risk, explaining predictions, and detecting anomalous updates.

## Components
1. `/data` - Synthetic dataset generator for training.
2. `/features` - Feature engineering pipeline with strict leakage tests.
3. `/training` - Training, hyperparameter tuning, and evaluating models via a rolling-origin time split.
4. `/explain` - SHAP explanations and a plain-language translator.
5. `/anomaly` - Unsupervised Isolation Forest for detecting data spikes and anomalous updates.
6. `/registry` - Contains trained models, model cards, and artifacts.
7. `/inference` - Exposes `run_inference`, the single backend contract.

## End-to-End Pipeline
To run the full training pipeline from scratch:

1. **Generate Synthetic Data**:
   ```bash
   python backend/ml_core/data/generator.py
   ```
   *Generates `dataset.csv` with ~2,000 projects.*

2. **Build Temporal Features**:
   ```bash
   python backend/ml_core/build_features.py
   ```
   *Extracts point-in-time features ensuring no data leakage, saving train/val/test splits to `backend/ml_core/data/processed/`.*

3. **Train Predictive Models**:
   ```bash
   python backend/ml_core/training/train.py
   ```
   *Trains Logistic Regression, Random Forest, XGBoost, and CatBoost. Selects best model (optimized for PR-AUC), calibrates probabilities, and saves to registry.*

4. **Train Anomaly Detector**:
   ```bash
   python backend/ml_core/anomaly/detector.py
   ```
   *Trains the Isolation Forest on update-to-update deltas.*

## Running Inference
The API contract is exposed in `backend/ml_core/inference/infer.py`. 

```python
import pandas as pd
from backend.ml_core.inference.infer import run_inference

# historical_updates_df is a pandas DataFrame of all updates up to as_of_date for ONE project
result = run_inference(
    project_id="PRJ-1001",
    as_of_date="2024-05-01",
    project_updates_df=historical_updates_df
)
print(result)
```

The result dictionary contains:
- `p_cost`: Probability of cost overrun
- `p_time`: Probability of time delay
- `p_impl`: Probability of implementation risk
- `composite_risk_score`: Weighted risk
- `risk_band`: High/Medium/Low
- `shap_explanation`: List of top 5 SHAP features with plain English translations
- `anomaly_score`: 0.0 - 1.0 score
- `anomaly_triggers`: List of rules triggered
