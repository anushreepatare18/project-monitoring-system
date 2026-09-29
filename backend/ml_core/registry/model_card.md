# Model Card: PRAGYA AI Core Models
    
## Selections
- **Cost Overrun Target (`label_overrun`)**: CatBoost
- **Time Delay Target (`label_delay`)**: CatBoost
- **Implementation Risk Target (`label_impl_risk`)**: CatBoost

## Intended Use
Early warning risk detection for government infrastructure projects.
Models predict outcomes based on physical progress, financials, and milestone delays.
Human-in-the-loop validation is MANDATORY.

## Evaluation
See `*_metrics.json` for detailed PR-AUC, Recall, Precision and Brier scores evaluated on rolling unseen temporal holds.
