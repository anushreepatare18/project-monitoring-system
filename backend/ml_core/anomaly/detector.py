import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import pickle
import os

class AnomalyDetector:
    def __init__(self, random_state=42):
        self.iso_forest = IsolationForest(contamination=0.05, random_state=random_state)
        self.is_fitted = False
        
    def _compute_deltas(self, project_updates: pd.DataFrame):
        """
        Computes update-to-update deltas for a single project's history.
        Assumes project_updates is sorted by date.
        """
        if len(project_updates) < 2:
            return pd.DataFrame()
            
        df = project_updates.copy()
        
        # Calculate deltas
        df['prog_jump'] = df['physical_progress_pct'].diff().fillna(0)
        df['exp_spike'] = df['cumulative_expenditure'].diff().fillna(0)
        
        # For dates, calculate days shift in expected completion
        df['expected_completion_date'] = pd.to_datetime(df['expected_completion_date'])
        df['date_shift_days'] = df['expected_completion_date'].diff().dt.days.fillna(0)
        
        # Calculate time between updates to normalize jumps
        df['update_date'] = pd.to_datetime(df['update_date'])
        df['days_since_last'] = df['update_date'].diff().dt.days.replace(0, 1) # Avoid div by zero
        
        df['prog_velocity'] = df['prog_jump'] / df['days_since_last']
        df['exp_velocity'] = df['exp_spike'] / df['days_since_last']
        
        # Only return the rows where we actually have a previous state to compare to (i.e. not the first row)
        return df.iloc[1:]
        
    def fit(self, dataset: pd.DataFrame):
        """
        Fits the IsolationForest on historical deltas across all projects.
        """
        all_deltas = []
        for pid, grp in dataset.groupby('project_id'):
            grp_sorted = grp.sort_values('update_date')
            deltas = self._compute_deltas(grp_sorted)
            if not deltas.empty:
                all_deltas.append(deltas)
                
        if not all_deltas:
            print("Not enough data to train anomaly detector.")
            return
            
        full_deltas = pd.concat(all_deltas, ignore_index=True)
        features = full_deltas[['prog_velocity', 'exp_velocity', 'date_shift_days']].fillna(0)
        
        self.iso_forest.fit(features)
        self.is_fitted = True
        
        # Save model
        os.makedirs('backend/ml_core/registry', exist_ok=True)
        with open('backend/ml_core/registry/anomaly_detector.pkl', 'wb') as f:
            pickle.dump(self, f)
            
        print("Anomaly detector trained and saved.")
        
    def detect(self, project_updates: pd.DataFrame):
        """
        Runs anomaly detection on the LATEST update of a project.
        project_updates must contain at least the 2 most recent updates.
        Returns (is_anomalous: bool, score: float, triggers: list)
        """
        if not self.is_fitted:
            raise ValueError("Model is not fitted. Train first or load from registry.")
            
        if len(project_updates) < 2:
            return False, 0.0, []
            
        grp_sorted = project_updates.sort_values('update_date')
        deltas = self._compute_deltas(grp_sorted)
        latest_delta = deltas.iloc[-1:]
        
        features = latest_delta[['prog_velocity', 'exp_velocity', 'date_shift_days']].fillna(0)
        
        # Iso forest predict: -1 for outliers, 1 for inliers
        prediction = self.iso_forest.predict(features)[0]
        score = self.iso_forest.score_samples(features)[0] # Lower score = more anomalous
        
        # Normalize score somewhat to [0, 1] where 1 is highly anomalous
        # (Assuming typical scores range from roughly -0.8 to -0.3)
        normalized_score = min(1.0, max(0.0, (-score - 0.3) / 0.5))
        
        is_ml_anomalous = (prediction == -1)
        triggers = []
        
        # ML Triggers based on feature values if anomalous
        if is_ml_anomalous:
            prog_v = features['prog_velocity'].iloc[0]
            if prog_v > 1.0: # Very fast progress
                triggers.append("Implausible jump in physical progress")
            elif prog_v < 0:
                triggers.append("Negative progress reported")
                
            exp_v = features['exp_velocity'].iloc[0]
            # Since expenditure scale varies, we just use a generic flag if ML caught it and it's large
            if abs(exp_v) > latest_delta['sanctioned_cost'].iloc[0] * 0.1: # Jumped 10% of total cost in one update
                triggers.append("Sudden spike in expenditure")
                
            date_shift = features['date_shift_days'].iloc[0]
            if abs(date_shift) > 365:
                triggers.append("Expected completion date shifted by over a year")
                
        # Rule-based checks (independent of ML model)
        latest = grp_sorted.iloc[-1]
        
        if latest['cumulative_expenditure'] > latest['sanctioned_cost'] * 2.0:
            triggers.append("Expenditure is more than double the sanctioned cost")
            normalized_score = max(normalized_score, 0.9)
            
        if latest['physical_progress_pct'] > 100 or latest['physical_progress_pct'] < 0:
            triggers.append("Physical progress percentage out of bounds [0-100]")
            normalized_score = 1.0
            
        is_anomalous = is_ml_anomalous or len(triggers) > 0
        
        return is_anomalous, float(normalized_score), list(set(triggers))

if __name__ == "__main__":
    print("Training anomaly detector on dataset.csv...")
    try:
        df = pd.read_csv("dataset.csv")
        detector = AnomalyDetector()
        detector.fit(df)
    except Exception as e:
        print(f"Failed to train anomaly detector: {e}")
