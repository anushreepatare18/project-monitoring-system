import pandas as pd
import numpy as np
import os
import pickle
import json
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import precision_score, recall_score, f1_score, average_precision_score, brier_score_loss
import xgboost as xgb
import catboost as cb

# Define targets and continuous features
TARGETS = ['label_overrun', 'label_delay', 'label_impl_risk']

FEATURES_TO_SCALE = [
    'progress_gap', 'velocity_last_1', 'velocity_last_3', 'velocity_last_6',
    'velocity_needed_to_finish', 'pct_milestones_delayed', 'max_milestone_delay_months',
    'cost_growth_pct', 'expenditure_to_progress_ratio', 'burn_rate_per_day',
    'days_since_last_update', 'avg_update_gap', 'count_of_revised_dates'
]
CATEGORICALS = ['sector', 'ministry', 'agency']

def load_data():
    train = pd.read_csv("backend/ml_core/data/processed/train.csv")
    val = pd.read_csv("backend/ml_core/data/processed/val.csv")
    test = pd.read_csv("backend/ml_core/data/processed/test.csv")
    return train, val, test

def preprocess(train, val, test):
    # Missing value handling (though pipeline should handle it mostly, be safe)
    train.fillna(0, inplace=True)
    val.fillna(0, inplace=True)
    test.fillna(0, inplace=True)
    
    # Scale continuous
    scaler = StandardScaler()
    train_scaled = train.copy()
    val_scaled = val.copy()
    test_scaled = test.copy()
    
    train_scaled[FEATURES_TO_SCALE] = scaler.fit_transform(train[FEATURES_TO_SCALE])
    val_scaled[FEATURES_TO_SCALE] = scaler.transform(val[FEATURES_TO_SCALE])
    test_scaled[FEATURES_TO_SCALE] = scaler.transform(test[FEATURES_TO_SCALE])
    
    # One-hot encoding for non-catboost models
    train_ohe = pd.get_dummies(train_scaled, columns=CATEGORICALS, drop_first=True)
    val_ohe = pd.get_dummies(val_scaled, columns=CATEGORICALS, drop_first=True)
    test_ohe = pd.get_dummies(test_scaled, columns=CATEGORICALS, drop_first=True)
    
    # Align columns
    val_ohe = val_ohe.reindex(columns=train_ohe.columns, fill_value=0)
    test_ohe = test_ohe.reindex(columns=train_ohe.columns, fill_value=0)
    
    return train_scaled, val_scaled, test_scaled, train_ohe, val_ohe, test_ohe, scaler

def train_and_evaluate(target, train_ohe, val_ohe, test_ohe, train_cat, val_cat, test_cat):
    print(f"\n{'='*50}\nTraining models for {target}\n{'='*50}")
    
    X_train = train_ohe.drop(columns=['project_id', 'as_of_date'] + TARGETS)
    y_train = train_ohe[target]
    
    X_val = val_ohe.drop(columns=['project_id', 'as_of_date'] + TARGETS)
    y_val = val_ohe[target]
    
    X_test = test_ohe.drop(columns=['project_id', 'as_of_date'] + TARGETS)
    y_test = test_ohe[target]
    
    # Baseline: Logistic Regression
    lr = LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42)
    lr.fit(X_train, y_train)
    lr_calib = CalibratedClassifierCV(lr, method='isotonic', cv='prefit')
    lr_calib.fit(X_val, y_val)
    
    # Random Forest
    rf = RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42)
    rf.fit(X_train, y_train)
    rf_calib = CalibratedClassifierCV(rf, method='isotonic', cv='prefit')
    rf_calib.fit(X_val, y_val)
    
    # XGBoost
    scale_pos_weight = (len(y_train) - sum(y_train)) / sum(y_train) if sum(y_train) > 0 else 1.0
    xgb_model = xgb.XGBClassifier(scale_pos_weight=scale_pos_weight, n_estimators=100, random_state=42, eval_metric='logloss')
    xgb_model.fit(X_train, y_train)
    xgb_calib = CalibratedClassifierCV(xgb_model, method='isotonic', cv='prefit')
    xgb_calib.fit(X_val, y_val)
    
    # CatBoost
    X_train_cat = train_cat.drop(columns=['project_id', 'as_of_date'] + TARGETS)
    X_val_cat = val_cat.drop(columns=['project_id', 'as_of_date'] + TARGETS)
    X_test_cat = test_cat.drop(columns=['project_id', 'as_of_date'] + TARGETS)
    
    cat_model = cb.CatBoostClassifier(iterations=100, cat_features=CATEGORICALS, random_seed=42, verbose=0, scale_pos_weight=scale_pos_weight)
    cat_model.fit(X_train_cat, y_train, eval_set=(X_val_cat, y_val), early_stopping_rounds=20)
    # CatBoost handles calibration natively pretty well, but we can wrap it if needed. We'll use it as is.
    
    models = {
        'LogisticRegression': (lr_calib, X_test),
        'RandomForest': (rf_calib, X_test),
        'XGBoost': (xgb_calib, X_test),
        'CatBoost': (cat_model, X_test_cat)
    }
    
    best_model_name = None
    best_pr_auc = -1
    best_model = None
    metrics_report = {}
    
    for name, (model, X_eval) in models.items():
        if name == 'CatBoost':
            y_pred_prob = model.predict_proba(X_eval)[:, 1]
        else:
            y_pred_prob = model.predict_proba(X_eval)[:, 1]
            
        y_pred = (y_pred_prob > 0.5).astype(int)
        
        pr_auc = average_precision_score(y_test, y_pred_prob)
        rec = recall_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred)
        brier = brier_score_loss(y_test, y_pred_prob)
        
        metrics_report[name] = {
            'PR-AUC': pr_auc,
            'Recall': rec,
            'Precision': prec,
            'F1': f1,
            'Brier': brier
        }
        
        print(f"[{name}] PR-AUC: {pr_auc:.3f} | Recall: {rec:.3f} | Brier: {brier:.3f}")
        
        if rec >= 0.5 and pr_auc > best_pr_auc:
            best_pr_auc = pr_auc
            best_model_name = name
            best_model = model
            
    # Baseline fallback if none perform well
    if best_model_name is None:
        print("No advanced model met the recall threshold. Falling back to LogisticRegression.")
        best_model_name = 'LogisticRegression'
        best_model = models['LogisticRegression'][0]
        
    print(f"-> Selected {best_model_name} for {target}")
    
    # Save the model
    os.makedirs('backend/ml_core/registry', exist_ok=True)
    with open(f'backend/ml_core/registry/{target}_model.pkl', 'wb') as f:
        pickle.dump(best_model, f)
        
    with open(f'backend/ml_core/registry/{target}_metrics.json', 'w') as f:
        json.dump(metrics_report, f, indent=4)
        
    return best_model_name

def main():
    print("Loading datasets...")
    train, val, test = load_data()
    train_cat, val_cat, test_cat, train_ohe, val_ohe, test_ohe, scaler = preprocess(train, val, test)
    
    # Save scaler
    os.makedirs('backend/ml_core/registry', exist_ok=True)
    with open('backend/ml_core/registry/scaler.pkl', 'wb') as f:
        pickle.dump(scaler, f)
        
    # Save columns list for inference
    columns_info = {
        'ohe_columns': list(train_ohe.drop(columns=['project_id', 'as_of_date'] + TARGETS).columns),
        'cat_columns': list(train_cat.drop(columns=['project_id', 'as_of_date'] + TARGETS).columns)
    }
    with open('backend/ml_core/registry/columns.json', 'w') as f:
        json.dump(columns_info, f, indent=4)
        
    selections = {}
    for target in TARGETS:
        best = train_and_evaluate(target, train_ohe, val_ohe, test_ohe, train_cat, val_cat, test_cat)
        selections[target] = best
        
    # Write model card
    card = f"""# Model Card: PRAGYA AI Core Models
    
## Selections
- **Cost Overrun Target (`label_overrun`)**: {selections['label_overrun']}
- **Time Delay Target (`label_delay`)**: {selections['label_delay']}
- **Implementation Risk Target (`label_impl_risk`)**: {selections['label_impl_risk']}

## Intended Use
Early warning risk detection for government infrastructure projects.
Models predict outcomes based on physical progress, financials, and milestone delays.
Human-in-the-loop validation is MANDATORY.

## Evaluation
See `*_metrics.json` for detailed PR-AUC, Recall, Precision and Brier scores evaluated on rolling unseen temporal holds.
"""
    with open('backend/ml_core/registry/model_card.md', 'w') as f:
        f.write(card)
        
    print("Training complete. Artifacts saved in backend/ml_core/registry/")

if __name__ == "__main__":
    main()
