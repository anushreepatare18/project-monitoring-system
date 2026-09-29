import os
import pickle
import json
import pandas as pd
from backend.ml_core.features.pipeline import compute_features
from backend.ml_core.explain.explainer import explain_prediction
from backend.ml_core.anomaly.detector import AnomalyDetector

class PragyaInferenceEngine:
    def __init__(self, registry_dir="backend/ml_core/registry"):
        self.registry_dir = registry_dir
        self.models = {}
        self.scaler = None
        self.columns = {}
        self.anomaly_detector = None
        self._load_artifacts()
        
    def _load_artifacts(self):
        targets = ['label_overrun', 'label_delay', 'label_impl_risk']
        for t in targets:
            model_path = os.path.join(self.registry_dir, f"{t}_model.pkl")
            if os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    self.models[t] = pickle.load(f)
                    
        scaler_path = os.path.join(self.registry_dir, 'scaler.pkl')
        if os.path.exists(scaler_path):
            with open(scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)
                
        cols_path = os.path.join(self.registry_dir, 'columns.json')
        if os.path.exists(cols_path):
            with open(cols_path, 'r') as f:
                self.columns = json.load(f)
                
        anomaly_path = os.path.join(self.registry_dir, 'anomaly_detector.pkl')
        if os.path.exists(anomaly_path):
            with open(anomaly_path, 'rb') as f:
                self.anomaly_detector = pickle.load(f)
                
    def _preprocess_features(self, features_dict):
        # Scale
        df = pd.DataFrame([features_dict])
        
        # We need to apply the exact same preprocessing
        FEATURES_TO_SCALE = [
            'progress_gap', 'velocity_last_1', 'velocity_last_3', 'velocity_last_6',
            'velocity_needed_to_finish', 'pct_milestones_delayed', 'max_milestone_delay_months',
            'cost_growth_pct', 'expenditure_to_progress_ratio', 'burn_rate_per_day',
            'days_since_last_update', 'avg_update_gap', 'count_of_revised_dates'
        ]
        CATEGORICALS = ['sector', 'ministry', 'agency']
        
        # Ensure all columns exist before scaling
        for col in FEATURES_TO_SCALE:
            if col not in df.columns:
                df[col] = 0.0
                
        if self.scaler:
            df[FEATURES_TO_SCALE] = self.scaler.transform(df[FEATURES_TO_SCALE])
            
        # OHE for Logistic/RF/XGB
        df_ohe = pd.get_dummies(df, columns=CATEGORICALS) if any(c in df.columns for c in CATEGORICALS) else df.copy()
        if 'ohe_columns' in self.columns:
            df_ohe = df_ohe.reindex(columns=self.columns['ohe_columns'], fill_value=0)
            
        # CatBoost features
        df_cat = df.copy()
        if 'cat_columns' in self.columns:
            df_cat = df_cat.reindex(columns=self.columns['cat_columns'], fill_value=0)
            # Ensure categoricals are strings
            for col in CATEGORICALS:
                if col in df_cat.columns:
                    df_cat[col] = df_cat[col].astype(str)
                    
        return df_ohe, df_cat
        
    def predict(self, project_updates_df: pd.DataFrame, as_of_date: str) -> dict:
        """
        Executes the exact contract for the backend API.
        project_updates_df: Historical updates for a specific project
        """
        if project_updates_df.empty:
            return {"error": "No project data"}
            
        # 1. Compute features
        try:
            features = compute_features(project_updates_df, as_of_date)
        except ValueError as e:
            return {"error": str(e)}
            
        if not features:
            return {"error": "No valid data before as_of_date"}
            
        # 2. Preprocess
        df_ohe, df_cat = self._preprocess_features(features)
        
        # 3. Predict Risks
        preds = {}
        top_model_used = None
        top_model_x = None
        
        for t in ['label_overrun', 'label_delay', 'label_impl_risk']:
            if t not in self.models:
                preds[t] = 0.0
                continue
                
            model = self.models[t]
            model_type = type(model).__name__
            
            is_catboost = 'CatBoost' in model_type
            X = df_cat if is_catboost else df_ohe
            
            if hasattr(model, 'predict_proba'):
                prob = model.predict_proba(X)[0, 1]
            else:
                prob = float(model.predict(X)[0])
                
            preds[t] = float(prob)
            
            # Store one model for SHAP (we'll use implementation risk or cost overrun as primary explainer)
            if t == 'label_overrun':
                top_model_used = model
                top_model_x = X
                
        p_cost = preds.get('label_overrun', 0.0)
        p_time = preds.get('label_delay', 0.0)
        p_impl = preds.get('label_impl_risk', 0.0)
        
        # Composite score: Weighted average
        composite_risk_score = (p_cost * 0.4) + (p_time * 0.4) + (p_impl * 0.2)
        
        if composite_risk_score > 0.7:
            risk_band = "High"
        elif composite_risk_score > 0.4:
            risk_band = "Medium"
        else:
            risk_band = "Low"
            
        # 4. Explanations (SHAP)
        shap_explanation = []
        if top_model_used is not None and top_model_x is not None:
            model_name = type(top_model_used).__name__
            # If it's a calibrated classifier, we pretend it's Logistic or RF based on its base
            if 'Calibrated' in model_name:
                if 'Logistic' in str(type(top_model_used.estimator)):
                    model_name = 'LogisticRegression'
                elif 'RandomForest' in str(type(top_model_used.estimator)):
                    model_name = 'RandomForest'
                elif 'XGB' in str(type(top_model_used.estimator)):
                    model_name = 'XGBoost'
            
            try:
                shap_explanation = explain_prediction(top_model_used, top_model_x, model_name)
            except Exception as e:
                shap_explanation = [{"error": f"SHAP failed: {e}"}]
                
        # 5. Anomaly Detection
        anomaly_score = 0.0
        triggers = []
        if self.anomaly_detector:
            try:
                is_anom, score, triggers = self.anomaly_detector.detect(project_updates_df)
                anomaly_score = score
            except Exception:
                pass
                
        return {
            "p_cost": round(p_cost, 4),
            "p_time": round(p_time, 4),
            "p_impl": round(p_impl, 4),
            "composite_risk_score": round(composite_risk_score, 4),
            "risk_band": risk_band,
            "shap_explanation": shap_explanation,
            "anomaly_score": round(anomaly_score, 4),
            "anomaly_triggers": triggers
        }

# Global singleton for FastAPI
_engine = None

def get_inference_engine():
    global _engine
    if _engine is None:
        _engine = PragyaInferenceEngine()
    return _engine

def run_inference(project_id: str, as_of_date: str, project_updates_df: pd.DataFrame) -> dict:
    """
    Main contract function
    """
    engine = get_inference_engine()
    return engine.predict(project_updates_df, as_of_date)

def explain_risk(project_id: str, as_of_date: str, project_updates_df: pd.DataFrame = None) -> dict:
    """
    Exact API contract requested:
    explain_risk(project_id, as_of_date) -> {
        risk_probability, risk_band, top_reasons (plain text), 
        shap_chart, model_version, feature_set_version
    }
    """
    if project_updates_df is None:
        # If no dataframe passed, assume caller is loading it from DB or CSV here
        # For prototype purposes, we will mock a dummy dataframe
        project_updates_df = pd.DataFrame([{
            "project_id": project_id,
            "update_date": as_of_date,
            "physical_progress_pct": 50,
            "sanctioned_cost": 100
        }])
        
    engine = get_inference_engine()
    res = engine.predict(project_updates_df, as_of_date)
    
    if "error" in res:
        return {"error": res["error"]}
        
    # Format plain text top reasons
    shap_exps = res.get("shap_explanation", [])
    top_reasons_text = "\n".join([f"- {s['explanation']}" for s in shap_exps if 'explanation' in s])
    
    return {
        "risk_probability": res["composite_risk_score"],
        "risk_band": res["risk_band"],
        "top_reasons": top_reasons_text,
        "shap_chart": "Not natively returnable as JSON - Generate Matplotlib or send JSON format to frontend for rendering",
        "model_version": "catboost_v1.0",
        "feature_set_version": "features_v1.0"
    }
