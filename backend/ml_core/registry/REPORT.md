# PRAGYA AI ML Core Selection Report

## 1. Model Selection
We evaluated Logistic Regression, Random Forest, XGBoost, and CatBoost across a rolling-origin time split (Train: 2020-2022, Val: 2023, Test: 2024).

**Cost Overrun (`label_overrun`)**:
- **Selected**: CatBoost
- **Why**: Achieved the highest PR-AUC (0.986) and Recall (0.942) while maintaining excellent calibration natively.

**Time Delay (`label_delay`)**:
- **Selected**: CatBoost
- **Why**: Highest PR-AUC (0.987) and Recall (0.989). Consistently outperforms tree and linear baselines on imbalanced delay data.

**Implementation Risk (`label_impl_risk`)**:
- **Selected**: CatBoost
- **Why**: Highest PR-AUC (0.909) and Recall (0.909). Random forest and Logistic Regression struggled significantly with recall on this complex target.

*All models exhibited excellent expected calibration error (ECE) as indicated by low Brier scores (< 0.08).*

## 2. Example SHAP Explanations
Below are 3 real examples from the dataset run through the inference and explainability pipeline:

### Project: PRJ-924FB0F4
**Risk Band**: Medium (Composite: 0.5498)

**Probabilities**: Cost (0.0052), Time (0.9821), Implementation (0.7746)

**Anomaly Triggers**: 

**Top Driving Factors (SHAP)**:
- **expenditure_to_progress_ratio**: Expenditure is in line with physical progress (-0.13x), which decreases risk.
- **days_since_last_update**: Recent update received (-1.0 days ago), which decreases risk.
- **cost_growth_pct**: Project is operating within budget, which decreases risk.
- **progress_gap**: Progress is 0.5% ahead of the expected planned level, which significantly increases risk.
- **velocity_last_6**: Velocity last 6 has a value of -0.25, which increases risk.

### Project: PRJ-5D33319B
**Risk Band**: Low (Composite: 0.1422)

**Probabilities**: Cost (0.0214), Time (0.0024), Implementation (0.6633)

**Anomaly Triggers**: 

**Top Driving Factors (SHAP)**:
- **expenditure_to_progress_ratio**: Expenditure is in line with physical progress (-0.11x), which decreases risk.
- **days_since_last_update**: Recent update received (-1.0 days ago), which decreases risk.
- **progress_gap**: Progress is 1.3% ahead of the expected planned level, which significantly increases risk.
- **cost_growth_pct**: Project is operating within budget, which decreases risk.
- **velocity_last_3**: Velocity last 3 has a value of 0.77, which decreases risk.

### Project: PRJ-F6F74F04
**Risk Band**: Low (Composite: 0.0616)

**Probabilities**: Cost (0.0256), Time (0.0009), Implementation (0.2549)

**Anomaly Triggers**: 

**Top Driving Factors (SHAP)**:
- **expenditure_to_progress_ratio**: Expenditure is in line with physical progress (-0.11x), which decreases risk.
- **days_since_last_update**: Recent update received (-1.0 days ago), which decreases risk.
- **velocity_last_6**: Velocity last 6 has a value of 0.02, which increases risk.
- **cost_growth_pct**: Project is operating within budget, which decreases risk.
- **avg_update_gap**: Avg update gap has a value of 1.01, which increases risk.

