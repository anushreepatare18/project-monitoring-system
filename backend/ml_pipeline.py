import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score, recall_score, f1_score, average_precision_score
import xgboost as xgb
import catboost as cb
import shap
import pickle
import os

DATA_PATH = "project_data.csv"
MODEL_PATH = "risk_model.pkl"

def load_and_preprocess(filepath):
    # FR-1, FR-2: Ingestion & validation
    df = pd.read_csv(filepath)
    
    # Fill missing values
    df['Delay_Months'] = df['Delay_Months'].fillna(0)
    df['Cost_Overrun_Pct'] = df['Cost_Overrun_Pct'].fillna(0)
    df['Physical_Progress_Pct'] = df['Physical_Progress_Pct'].fillna(0)
    
    # FR-4: Feature Engineering
    # Calculate derived features
    df['Budget_Utilization'] = np.where(df['Original_Cost_Cr'] > 0, 
                                        df['Expenditure_Cr'] / df['Original_Cost_Cr'], 0)
    
    # Define features and target (FR-6, FR-7, FR-8)
    features = ['Original_Cost_Cr', 'Expenditure_Cr', 'Physical_Progress_Pct', 'Delay_Months', 'Cost_Overrun_Pct', 'Budget_Utilization']
    X = df[features]
    y = df['Is_High_Risk']
    
    return X, y, df

def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    
    # FR-13: evaluate models using Precision, Recall, F1, PR-AUC
    metrics = {
        'precision': precision_score(y_test, y_pred, zero_division=0),
        'recall': recall_score(y_test, y_pred, zero_division=0),
        'f1': f1_score(y_test, y_pred, zero_division=0),
        'pr_auc': average_precision_score(y_test, y_prob)
    }
    return metrics

def train_and_select_best_model():
    X, y, df = load_and_preprocess(DATA_PATH)
    
    # Time-based/Random split (FR-5 leakage prevention)
    # Using random split for prototype, but in real scenario would split by Date
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # FR-9: Compare multiple model types
    models = {
        "LogisticRegression": LogisticRegression(max_iter=1000, random_state=42),
        "RandomForest": RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42),
        "XGBoost": xgb.XGBClassifier(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42),
        "CatBoost": cb.CatBoostClassifier(iterations=100, depth=5, learning_rate=0.1, random_seed=42, verbose=0)
    }
    
    best_model = None
    best_score = -1
    best_name = ""
    
    for name, model in models.items():
        print(f"Training {name}...")
        model.fit(X_train, y_train)
        metrics = evaluate_model(model, X_test, y_test)
        print(f"{name} Metrics: {metrics}")
        
        # We select based on PR-AUC
        if metrics['pr_auc'] > best_score:
            best_score = metrics['pr_auc']
            best_model = model
            best_name = name
            
    print(f"\nBest model selected: {best_name} with PR-AUC: {best_score:.4f}")
    
    # Save the best model
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(best_model, f)
        
    print("Model trained and saved to", MODEL_PATH)
    return best_model, X

if __name__ == "__main__":
    best_model, X = train_and_select_best_model()
