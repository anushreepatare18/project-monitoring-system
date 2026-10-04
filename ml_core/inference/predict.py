"""
PRAGYA AI — Inference Contract  (v2)
======================================
Single callable entry point consumed by the backend API and chatbot.

Public API:
    predict_project(project_id, as_of_date, df_history) -> dict
    explain_risk(project_id, as_of_date, df_history)    -> dict   ← dashboard contract
"""
from __future__ import annotations

import json
import pickle
from datetime import date
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from ml_core.anomaly.detector import detect_anomalies
from ml_core.explain.shap_explainer import explain_global, explain_prediction
from ml_core.features.pipeline import (
    FEATURE_SET_VERSION,
    compute_features,
)

REGISTRY_DIR = Path("ml_core/registry")
MODEL_VERSION_DEFAULT = "v2.0.0"


# ── Model loading (cached in module scope) ────────────────────────────────────

_model_cache: dict[str, dict] = {}


def _load_model(target: str) -> Optional[dict]:
    """Load a pickled model dict from the registry. Cached after first load."""
    if target in _model_cache:
        return _model_cache[target]
    path = REGISTRY_DIR / f"{target}_best_model.pkl"
    if not path.exists():
        return None
    with open(path, "rb") as fh:
        payload = pickle.load(fh)
    _model_cache[target] = payload
    return payload


def _get_model_version(target: str) -> str:
    payload = _load_model(target)
    if payload:
        return payload.get("model_version", MODEL_VERSION_DEFAULT)
    return MODEL_VERSION_DEFAULT


# ── Risk-band helper ──────────────────────────────────────────────────────────

def _band(score: float) -> str:
    if score > 0.70:
        return "Critical"
    if score > 0.40:
        return "High"
    if score > 0.20:
        return "Medium"
    return "Low"


# ── Main inference function ───────────────────────────────────────────────────

def predict_project(
    project_id: str,
    as_of_date: str,
    df_history: pd.DataFrame,
) -> dict:
    """
    Unified inference contract for the backend API.

    Parameters
    ----------
    project_id : str
        The project to score.
    as_of_date : str
        ISO-8601 date string. Features are computed using ONLY data ≤ this date.
    df_history : DataFrame
        Full multi-project update history (will be filtered to project_id here).

    Returns
    -------
    dict with keys:
        p_cost              float   cost-overrun probability
        p_time              float   time-delay probability
        p_impl              float   implementation-risk probability
        composite_risk_score float  weighted combination
        risk_band           str     Low / Medium / High / Critical
        shap_explanation    list    top-5 SHAP dicts with 'text' field
        shap_chart          str     path to per-project bar chart
        anomaly_score       float
        anomaly_reasons     str
        model_version       str
        feature_set_version str
        as_of_date          str
    """
    project_df = df_history[
        df_history["project_id"] == project_id
    ].copy()
    if len(project_df) == 0:
        raise ValueError(f"Project '{project_id}' not found in the provided history.")

    # 1. Compute features (leakage-safe)
    X = compute_features(project_df, as_of_date).reset_index(drop=True)
    drop_cols = [c for c in ["project_id", "update_date"] if c in X.columns]
    X_model = X.drop(columns=drop_cols, errors="ignore")

    # 2. Score all three targets
    def _score(target: str) -> tuple[float, Optional[object]]:
        payload = _load_model(target)
        if payload is None:
            return 0.0, None
        mdl = payload["model"]
        try:
            prob = float(mdl.predict_proba(X_model)[0][1])
        except Exception:
            prob = 0.0
        return prob, mdl

    p_cost, model_cost = _score("overrun_flag")
    p_time, model_time = _score("delayed_flag")
    p_impl, model_impl = _score("implementation_risk_flag")

    # 3. Composite risk score (weighted)
    composite = p_cost * 0.40 + p_time * 0.40 + p_impl * 0.20

    # 4. Primary SHAP explanation (use the highest-probability model)
    shap_explanation: list[dict] = []
    shap_chart: Optional[str] = None

    primary_model  = None
    primary_target = None
    if max(p_cost, p_time, p_impl) > 0:
        if p_cost >= p_time and p_cost >= p_impl:
            primary_model, primary_target = model_cost, "overrun_flag"
        elif p_time >= p_cost and p_time >= p_impl:
            primary_model, primary_target = model_time, "delayed_flag"
        else:
            primary_model, primary_target = model_impl, "implementation_risk_flag"

    if primary_model is not None:
        shap_explanation, shap_chart = explain_prediction(
            primary_model, X_model, primary_target or "risk", project_id=project_id
        )

    # 5. Anomaly detection (temporal guard applied inside detect_anomalies)
    anomaly_df = detect_anomalies(project_df, as_of_date=as_of_date)
    if len(anomaly_df) > 0:
        latest_a = anomaly_df.iloc[-1]
        anomaly_score   = float(latest_a.get("anomaly_score", 0.0))
        anomaly_reasons = str(latest_a.get("anomaly_reason", ""))
    else:
        anomaly_score   = 0.0
        anomaly_reasons = ""

    return {
        "p_cost":               p_cost,
        "p_time":               p_time,
        "p_impl":               p_impl,
        "composite_risk_score": composite,
        "risk_band":            _band(composite),
        "shap_explanation":     shap_explanation,
        "shap_chart":           shap_chart,
        "anomaly_score":        anomaly_score,
        "anomaly_reasons":      anomaly_reasons,
        "model_version":        _get_model_version(primary_target or "overrun_flag"),
        "feature_set_version":  FEATURE_SET_VERSION,
        "as_of_date":           as_of_date,
    }


def explain_risk(
    project_id: str,
    as_of_date: str,
    df_history: pd.DataFrame,
) -> dict:
    """
    Dashboard/chatbot contract.
    Returns: risk_probability, risk_band, top_reasons (plain text),
             shap_chart, model_version, feature_set_version.
    """
    res = predict_project(project_id, as_of_date, df_history)
    return {
        "risk_probability":    max(res["p_cost"], res["p_time"], res["p_impl"]),
        "risk_band":           res["risk_band"],
        "top_reasons":         [item["text"] for item in res["shap_explanation"]],
        "shap_chart":          res["shap_chart"],
        "model_version":       res["model_version"],
        "feature_set_version": res["feature_set_version"],
        "as_of_date":          res["as_of_date"],
        "anomaly_score":       res["anomaly_score"],
        "anomaly_reasons":     res["anomaly_reasons"],
    }
