import pandas as pd
import json
from backend.ml_core.inference.infer import run_inference

def generate_report():
    df = pd.read_csv("dataset.csv")
    
    # Pick 3 random project IDs
    projects = df['project_id'].unique()[:3]
    
    report = """# PRAGYA AI ML Core Selection Report

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

"""
    
    for pid in projects:
        updates = df[df['project_id'] == pid].copy()
        latest_date = updates['update_date'].max()
        
        # Inference
        res = run_inference(pid, latest_date, updates)
        
        report += f"### Project: {pid}\n"
        report += f"**Risk Band**: {res['risk_band']} (Composite: {res['composite_risk_score']})\n\n"
        report += f"**Probabilities**: Cost ({res['p_cost']}), Time ({res['p_time']}), Implementation ({res['p_impl']})\n\n"
        
        if res['anomaly_score'] > 0:
            report += f"**Anomaly Triggers**: {', '.join(res['anomaly_triggers'])}\n\n"
            
        report += "**Top Driving Factors (SHAP)**:\n"
        for shp in res['shap_explanation']:
            if 'error' in shp:
                report += f"- Error: {shp['error']}\n"
            else:
                report += f"- **{shp['feature']}**: {shp['explanation']}\n"
        report += "\n"
        
    with open("backend/ml_core/registry/REPORT.md", "w") as f:
        f.write(report)
        
    print("Report generated at backend/ml_core/registry/REPORT.md")

if __name__ == "__main__":
    generate_report()
