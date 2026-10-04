import pandas as pd
import numpy as np
import os
import pickle
import json
from sklearn.model_selection import TimeSeriesSplit
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from catboost import CatBoostClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import precision_score, recall_score, f1_score, average_precision_score, brier_score_loss, roc_auc_score
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

from ml_core.features.pipeline import compute_features

def create_time_splits(df):
    df['outcome_known_at'] = pd.to_datetime(df['outcome_known_at'])
    df_sorted = df.sort_values('outcome_known_at')
    
    total_len = len(df_sorted)
    train_end = int(total_len * 0.6)
    val_end = int(total_len * 0.8)
    
    train_df = df_sorted.iloc[:train_end]
    val_df = df_sorted.iloc[train_end:val_end]
    test_df = df_sorted.iloc[val_end:]
    
    return train_df, val_df, test_df

def build_preprocessing(cat_features, num_features, model_type="sklearn"):
    if model_type == "catboost":
        return "passthrough" # Catboost handles natively
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), num_features),
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), cat_features)
        ])
    return preprocessor

def evaluate_model(y_true, y_prob, threshold=0.5):
    y_pred = (y_prob >= threshold).astype(int)
    return {
        "pr_auc": average_precision_score(y_true, y_prob),
        "roc_auc": roc_auc_score(y_true, y_prob),
        "brier_score": brier_score_loss(y_true, y_prob),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0)
    }

def train_and_evaluate(target="overrun_flag"):
    print(f"--- Training models for {target} ---")
    df = pd.read_csv("ml_core/data/synthetic_projects.csv")
    
    # We want to predict outcomes using features at the LAST update before outcome is known.
    # For a real cross-sectional evaluation, we'd pick a random cutoff per project.
    # To keep it simple, we just use the last update of each project.
    
    latest_updates = df.groupby('project_id').tail(1).copy()
    
    train_df, val_df, test_df = create_time_splits(latest_updates)
    
    # Features
    X_train = compute_features(train_df, "2030-01-01").reset_index()
    X_val = compute_features(val_df, "2030-01-01").reset_index()
    X_test = compute_features(test_df, "2030-01-01").reset_index()
    
    y_train = train_df.set_index('project_id').loc[X_train['project_id']][target].values
    y_val = val_df.set_index('project_id').loc[X_val['project_id']][target].values
    y_test = test_df.set_index('project_id').loc[X_test['project_id']][target].values
    
    X_train = X_train.drop(columns=['project_id'])
    X_val = X_val.drop(columns=['project_id'])
    X_test = X_test.drop(columns=['project_id'])
    
    cat_features = ['sector', 'ministry', 'agency', 'state', 'project_type']
    num_features = [c for c in X_train.columns if c not in cat_features]
    
    models = {
        "LogisticRegression": Pipeline([
            ('prep', build_preprocessing(cat_features, num_features)),
            ('clf', LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42))
        ]),
        "RandomForest": Pipeline([
            ('prep', build_preprocessing(cat_features, num_features)),
            ('clf', RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42))
        ]),
        "XGBoost": Pipeline([
            ('prep', build_preprocessing(cat_features, num_features)),
            ('clf', XGBClassifier(scale_pos_weight=(len(y_train)-sum(y_train))/sum(y_train), random_state=42))
        ]),
        "CatBoost": CatBoostClassifier(cat_features=cat_features, auto_class_weights='Balanced', random_state=42, verbose=0)
    }
    
    results = {}
    best_model = None
    best_score = -1
    
    os.makedirs("ml_core/registry", exist_ok=True)
    
    for name, model in models.items():
        print(f"Training {name}...")
        model.fit(X_train, y_train)
        
        # Calibrate
        calibrated = CalibratedClassifierCV(estimator=model, method='isotonic', cv="prefit")
        calibrated.fit(X_val, y_val)
        
        y_prob = calibrated.predict_proba(X_test)[:, 1]
        metrics = evaluate_model(y_test, y_prob)
        results[name] = metrics
        
        # Selection: Best PR-AUC with minimum recall 0.5
        if metrics['recall'] >= 0.5 and metrics['pr_auc'] > best_score:
            best_score = metrics['pr_auc']
            best_model = (name, calibrated)
            
    # Fallback to LR if none meet recall floor
    if best_model is None:
        best_model = ("LogisticRegression", models["LogisticRegression"])
        best_score = results["LogisticRegression"]["pr_auc"]
        
    print(f"Best model for {target}: {best_model[0]} (PR-AUC: {best_score:.3f})")
    
    with open(f"ml_core/registry/{target}_best_model.pkl", "wb") as f:
        pickle.dump(best_model[1], f)
        
    with open(f"ml_core/registry/{target}_metrics.json", "w") as f:
        json.dump(results, f, indent=4)
        
if __name__ == "__main__":
    train_and_evaluate("overrun_flag")
    train_and_evaluate("delayed_flag")
