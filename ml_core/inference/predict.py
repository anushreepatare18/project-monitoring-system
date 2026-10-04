import pandas as pd
import pickle
import os
from ml_core.features.pipeline import compute_features
from ml_core.explain.shap_explainer import explain_prediction
from ml_core.anomaly.detector import detect_anomalies

def load_model(target):
    path = f"ml_core/registry/{target}_best_model.pkl"
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return pickle.load(f)

def predict_project(project_id: str, as_of_date: str, df_history: pd.DataFrame):
    """
    Contract for backend API.
    Returns: {
        'p_cost': float,
        'p_time': float,
        'p_impl': float, # Simulated for now if model missing
        'composite_risk_score': float,
        'risk_band': str,
        'shap_explanation': list,
        'anomaly_score': float,
        'anomaly_reasons': str
    }
    """
    # 1. Compute features safely up to as_of_date
    project_df = df_history[df_history['project_id'] == project_id]
    if len(project_df) == 0:
        raise ValueError("Project not found.")
        
    X = compute_features(project_df, as_of_date).reset_index(drop=True)
    
    # 2. Predict Targets
    model_cost = load_model("overrun_flag")
    model_time = load_model("delayed_flag")
    
    # Needs 2D array, Drop index columns
    drop_cols = ['project_id', 'update_date']
    X_model = X.drop(columns=[c for c in drop_cols if c in X.columns], errors='ignore')
    
    p_cost = model_cost.predict_proba(X_model)[0][1] if model_cost else 0.0
    p_time = model_time.predict_proba(X_model)[0][1] if model_time else 0.0
    p_impl = 0.0 # Placeholder for implementation_risk if not fully trained
    
    composite = (p_cost * 0.4) + (p_time * 0.4) + (p_impl * 0.2)
    
    if composite > 0.7:
        band = "Critical"
    elif composite > 0.4:
        band = "High"
    elif composite > 0.2:
        band = "Medium"
    else:
        band = "Low"
        
    # 3. Explain Primary Risk
    shap_explanation = []
    shap_chart = None
    if model_cost and p_cost > p_time:
        shap_explanation, shap_chart = explain_prediction(model_cost, X_model, "overrun_flag")
    elif model_time:
        shap_explanation, shap_chart = explain_prediction(model_time, X_model, "delayed_flag")
        
    # 4. Anomaly
    anomalous_df = detect_anomalies(project_df)
    
    # Filter to anomalies happening right at as_of_date
    recent_anomalies = anomalous_df[anomalous_df['update_date'] <= pd.to_datetime(as_of_date)]
    if len(recent_anomalies) > 0:
        latest_anomaly = recent_anomalies.iloc[-1]
        anomaly_score = float(latest_anomaly['anomaly_score'])
        anomaly_reasons = latest_anomaly['anomaly_reason']
    else:
        anomaly_score = 0.0
        anomaly_reasons = ""

    return {
        "p_cost": float(p_cost),
        "p_time": float(p_time),
        "p_impl": float(p_impl),
        "composite_risk_score": float(composite),
        "risk_band": band,
        "shap_explanation": shap_explanation,
        "shap_chart": shap_chart,
        "anomaly_score": anomaly_score,
        "anomaly_reasons": anomaly_reasons
    }

def explain_risk(project_id: str, as_of_date: str, df_history: pd.DataFrame):
    """
    Contract specifically requested by Dashboard.
    """
    res = predict_project(project_id, as_of_date, df_history)
    return {
        "risk_probability": max(res["p_cost"], res["p_time"]),
        "risk_band": res["risk_band"],
        "top_reasons": [item["text"] for item in res["shap_explanation"]],
        "shap_chart": res["shap_chart"],
        "model_version": "v1.0.0",
        "feature_set_version": "v1"
    }
