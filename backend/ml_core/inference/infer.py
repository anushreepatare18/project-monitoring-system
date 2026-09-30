"""
PRAGYA AI — Inference Engine (Task 7)

Single clean callable:
    run_inference(project_id, as_of_date, project_updates_df)
    → {p_cost, p_time, p_impl, composite_risk_score, risk_band,
       shap_explanation, anomaly_score, anomaly_triggers}

The PragyaInferenceEngine class is a singleton loaded once and reused
across all API requests.
"""

from __future__ import annotations

import json
import os
import pickle
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

from backend.ml_core.features.pipeline import (
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    compute_features,
)
from backend.ml_core.explain.explainer import explain_prediction
from backend.ml_core.anomaly.detector import AnomalyDetector

REGISTRY_DIR = "backend/ml_core/registry"
TARGETS      = ["label_overrun", "label_delay", "label_impl_risk"]

# Composite risk weights
WEIGHTS = {"label_overrun": 0.40, "label_delay": 0.40, "label_impl_risk": 0.20}

# Risk band thresholds
BAND_CRITICAL = 0.75
BAND_HIGH     = 0.55
BAND_MEDIUM   = 0.35


# ── Inference Engine ───────────────────────────────────────────────────────────

class PragyaInferenceEngine:
    """
    Loads all registry artifacts once and serves predictions.
    Thread-safe for read-only inference (FastAPI compatible).
    """

    def __init__(self, registry_dir: str = REGISTRY_DIR):
        self.registry_dir = registry_dir
        self.models: Dict[str, Any]  = {}
        self.scaler: Optional[StandardScaler] = None
        self.columns: Dict[str, List[str]]    = {}
        self.model_card: Dict[str, Any]       = {}
        self.anomaly_detector: Optional[AnomalyDetector] = None
        self._load_artifacts()

    # ── Artifact loading ──────────────────────────────────────────────────────

    def _load_artifacts(self):
        for t in TARGETS:
            path = os.path.join(self.registry_dir, f"{t}_model.pkl")
            if os.path.exists(path):
                with open(path, "rb") as f:
                    self.models[t] = pickle.load(f)

        scaler_path = os.path.join(self.registry_dir, "scaler.pkl")
        if os.path.exists(scaler_path):
            with open(scaler_path, "rb") as f:
                self.scaler = pickle.load(f)

        cols_path = os.path.join(self.registry_dir, "columns.json")
        if os.path.exists(cols_path):
            with open(cols_path, "r") as f:
                self.columns = json.load(f)

        card_path = os.path.join(self.registry_dir, "model_card.json")
        if os.path.exists(card_path):
            with open(card_path, "r") as f:
                self.model_card = json.load(f)

        anom_path = os.path.join(self.registry_dir, "anomaly_detector.pkl")
        if os.path.exists(anom_path):
            with open(anom_path, "rb") as f:
                self.anomaly_detector = pickle.load(f)

        loaded = list(self.models.keys())
        print(f"[PragyaEngine] Loaded models: {loaded or 'NONE (run training first)'}")

    @property
    def is_ready(self) -> bool:
        return len(self.models) >= len(TARGETS)

    # ── Preprocessing ─────────────────────────────────────────────────────────

    def _preprocess(
        self, features_dict: Dict[str, Any]
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Returns (X_ohe, X_cat) — two views of the same feature vector.
        """
        df = pd.DataFrame([features_dict])

        # Fill missing numerics
        for col in NUMERIC_FEATURES:
            if col not in df.columns:
                df[col] = 0.0

        # Scale numerics
        if self.scaler is not None:
            cols_to_scale = [c for c in NUMERIC_FEATURES if c in df.columns]
            df[cols_to_scale] = self.scaler.transform(df[cols_to_scale].fillna(0.0))

        # ── OHE version (LR / RF / XGB) ──────────────────────────────────
        cats_present = [c for c in CATEGORICAL_FEATURES if c in df.columns]
        df_ohe = pd.get_dummies(df, columns=cats_present, drop_first=False)
        if "ohe_columns" in self.columns and self.columns["ohe_columns"]:
            df_ohe = df_ohe.reindex(columns=self.columns["ohe_columns"], fill_value=0)

        # ── CatBoost version (raw strings) ────────────────────────────────
        df_cat = df.copy()
        for c in CATEGORICAL_FEATURES:
            if c in df_cat.columns:
                df_cat[c] = df_cat[c].astype(str)
        if "cat_columns" in self.columns and self.columns["cat_columns"]:
            df_cat = df_cat.reindex(columns=self.columns["cat_columns"], fill_value=0)

        return df_ohe, df_cat

    # ── Core prediction ───────────────────────────────────────────────────────

    def predict(
        self,
        project_updates_df: pd.DataFrame,
        as_of_date: str,
    ) -> Dict[str, Any]:
        """
        Full inference pipeline.

        Parameters
        ----------
        project_updates_df : pd.DataFrame
            Historical updates for exactly ONE project.
        as_of_date : str
            ISO date string 'YYYY-MM-DD'.

        Returns
        -------
        dict with keys:
            p_cost, p_time, p_impl, composite_risk_score, risk_band,
            shap_explanation, anomaly_score, anomaly_triggers,
            model_version, feature_set_version
        """
        if project_updates_df is None or project_updates_df.empty:
            return {"error": "No project update data provided."}

        # ── 1. Feature engineering ─────────────────────────────────────────
        try:
            features = compute_features(project_updates_df, as_of_date)
        except ValueError as exc:
            return {"error": str(exc)}

        if features is None:
            return {"error": f"No project data exists before {as_of_date}."}

        # ── 2. Preprocess ──────────────────────────────────────────────────
        X_ohe, X_cat = self._preprocess(features)

        # ── 3. Risk predictions ────────────────────────────────────────────
        probabilities: Dict[str, float] = {}
        shap_model: Optional[Any]       = None
        shap_X: Optional[pd.DataFrame]  = None

        for target in TARGETS:
            if target not in self.models:
                probabilities[target] = 0.0
                continue

            model = self.models[target]
            model_class = type(model).__name__

            # CatBoost models use raw categorical features
            is_catboost = "CatBoost" in model_class or (
                hasattr(model, "estimator") and "CatBoost" in type(model.estimator).__name__
            )
            X = X_cat if is_catboost else X_ohe

            try:
                prob = float(model.predict_proba(X)[0, 1])
            except Exception:
                prob = 0.0

            probabilities[target] = round(prob, 4)

            # Use cost-overrun model for SHAP (primary explainer)
            if target == "label_overrun":
                shap_model = model
                shap_X     = X

        p_cost = probabilities.get("label_overrun", 0.0)
        p_time = probabilities.get("label_delay",   0.0)
        p_impl = probabilities.get("label_impl_risk", 0.0)

        composite = round(
            p_cost * WEIGHTS["label_overrun"] +
            p_time * WEIGHTS["label_delay"]   +
            p_impl * WEIGHTS["label_impl_risk"],
            4,
        )

        if composite >= BAND_CRITICAL:
            risk_band = "Critical"
        elif composite >= BAND_HIGH:
            risk_band = "High"
        elif composite >= BAND_MEDIUM:
            risk_band = "Medium"
        else:
            risk_band = "Low"

        # ── 4. SHAP Explanation ────────────────────────────────────────────
        shap_explanation: List[Dict[str, Any]] = []
        if shap_model is not None and shap_X is not None:
            try:
                shap_explanation = explain_prediction(shap_model, shap_X, top_k=5)
            except Exception as exc:
                shap_explanation = [{"error": f"SHAP failed: {exc}"}]

        # ── 5. Anomaly Detection ───────────────────────────────────────────
        anomaly_score    = 0.0
        anomaly_triggers: List[str] = []
        if self.anomaly_detector is not None:
            try:
                _is_anom, anomaly_score, anomaly_triggers = (
                    self.anomaly_detector.detect(project_updates_df)
                )
            except Exception:
                pass

        return {
            "p_cost":               p_cost,
            "p_time":               p_time,
            "p_impl":               p_impl,
            "composite_risk_score": composite,
            "risk_band":            risk_band,
            "shap_explanation":     shap_explanation,
            "anomaly_score":        round(anomaly_score, 4),
            "anomaly_triggers":     anomaly_triggers,
            "model_version":        self.model_card.get("version", "unknown"),
            "feature_set_version":  self.columns.get("feature_set_version", "unknown"),
        }


# ── Singleton management ───────────────────────────────────────────────────────

_engine: Optional[PragyaInferenceEngine] = None


def get_inference_engine() -> PragyaInferenceEngine:
    global _engine
    if _engine is None:
        _engine = PragyaInferenceEngine()
    return _engine


def reset_engine():
    """Force reload of all registry artifacts (e.g., after re-training)."""
    global _engine
    _engine = None


# ── Public API contract ────────────────────────────────────────────────────────

def run_inference(
    project_id: str,
    as_of_date: str,
    project_updates_df: pd.DataFrame,
) -> Dict[str, Any]:
    """
    Main inference contract called by the backend API.

    Parameters
    ----------
    project_id : str
        Project identifier (used for audit logging only).
    as_of_date : str
        ISO date string e.g. '2023-06-01'.
    project_updates_df : pd.DataFrame
        All update rows for the project (may include future rows — leakage
        check inside compute_features will catch and reject them).

    Returns
    -------
    dict: {
        p_cost: float,          # P(cost overrun)
        p_time: float,          # P(time delay)
        p_impl: float,          # P(implementation risk)
        composite_risk_score: float,
        risk_band: str,         # 'Critical' | 'High' | 'Medium' | 'Low'
        shap_explanation: list[dict],
        anomaly_score: float,
        anomaly_triggers: list[str],
        model_version: str,
        feature_set_version: str,
    }
    """
    engine = get_inference_engine()
    result = engine.predict(project_updates_df, as_of_date)
    # Attach project_id for traceability
    result["project_id"] = project_id
    return result


def explain_risk(
    project_id: str,
    as_of_date: str,
    project_updates_df: Optional[pd.DataFrame] = None,
) -> Dict[str, Any]:
    """
    Convenience wrapper that formats the SHAP explanation as top plain-text reasons.
    Called directly by the FastAPI /api/projects/{id}/explanation endpoint.
    """
    if project_updates_df is None or project_updates_df.empty:
        return {"error": "No project data provided."}

    result = run_inference(project_id, as_of_date, project_updates_df)

    if "error" in result:
        return result

    shap_exps = result.get("shap_explanation", [])
    top_reasons = [
        s["explanation"] for s in shap_exps if "explanation" in s
    ]

    return {
        "project_id":          project_id,
        "as_of_date":          as_of_date,
        "risk_probability":    result["composite_risk_score"],
        "risk_band":           result["risk_band"],
        "p_cost":              result["p_cost"],
        "p_time":              result["p_time"],
        "p_impl":              result["p_impl"],
        "shap_explanations":   shap_exps,
        "top_reasons":         top_reasons,
        "anomaly_score":       result["anomaly_score"],
        "anomaly_triggers":    result["anomaly_triggers"],
        "model_version":       result.get("model_version", "unknown"),
        "feature_set_version": result.get("feature_set_version", "unknown"),
    }
