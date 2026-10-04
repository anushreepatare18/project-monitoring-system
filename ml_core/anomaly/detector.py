import pandas as pd
import numpy as np
import pickle
import os
from sklearn.ensemble import IsolationForest

def compute_deltas(df_history: pd.DataFrame) -> pd.DataFrame:
    """
    Computes update-to-update deltas for a project's history.
    """
    df = df_history.sort_values(by=['project_id', 'update_date']).copy()
    
    df['prev_physical'] = df.groupby('project_id')['physical_progress_pct'].shift(1)
    df['prev_financial'] = df.groupby('project_id')['financial_progress_pct'].shift(1)
    df['prev_expenditure'] = df.groupby('project_id')['cumulative_expenditure'].shift(1)
    
    df['delta_physical'] = df['physical_progress_pct'] - df['prev_physical']
    df['delta_financial'] = df['financial_progress_pct'] - df['prev_financial']
    df['delta_expenditure'] = df['cumulative_expenditure'] - df['prev_expenditure']
    
    # Drop first updates (no delta)
    df = df.dropna(subset=['delta_physical'])
    
    return df

def train_anomaly_detector():
    df = pd.read_csv("ml_core/data/synthetic_projects.csv")
    deltas = compute_deltas(df)
    
    features = ['delta_physical', 'delta_financial', 'delta_expenditure']
    X = deltas[features].fillna(0)
    
    iso = IsolationForest(contamination=0.05, random_state=42)
    iso.fit(X)
    
    os.makedirs("ml_core/registry", exist_ok=True)
    with open("ml_core/registry/anomaly_model.pkl", "wb") as f:
        pickle.dump(iso, f)
        
    print("Anomaly detector trained and saved.")

def detect_anomalies(df_history: pd.DataFrame):
    """
    Detects anomalies for the latest updates.
    Returns anomalous rows with reasons.
    """
    try:
        with open("ml_core/registry/anomaly_model.pkl", "rb") as f:
            iso = pickle.load(f)
    except FileNotFoundError:
        return pd.DataFrame()
        
    deltas = compute_deltas(df_history)
    if len(deltas) == 0:
        return pd.DataFrame()
        
    features = ['delta_physical', 'delta_financial', 'delta_expenditure']
    X = deltas[features].fillna(0)
    
    deltas['anomaly_score'] = iso.decision_function(X)
    deltas['is_anomaly'] = iso.predict(X) == -1
    
    anomalous = deltas[deltas['is_anomaly']].copy()
    
    reasons = []
    for _, row in anomalous.iterrows():
        reason = []
        if row['delta_physical'] < -5:
            reason.append("Implausible drop in physical progress.")
        if row['delta_expenditure'] > row['sanctioned_cost'] * 0.2:
            reason.append("Sudden expenditure spike.")
        if row['delta_financial'] - row['delta_physical'] > 20:
            reason.append("Financial progress significantly outpaces physical.")
            
        reasons.append(" | ".join(reason) if reason else "Unusual update pattern detected.")
        
    anomalous['anomaly_reason'] = reasons
    return anomalous

if __name__ == "__main__":
    train_anomaly_detector()
