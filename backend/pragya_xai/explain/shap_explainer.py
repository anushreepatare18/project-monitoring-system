"""
PRAGYA XAI — /explain/shap_explainer.py
SHAP computation, plain-English translation, per-project bar charts,
global feature importance chart, and the public explain_risk() function.
"""
from __future__ import annotations

import io
import json
import os
import pickle
import base64
from typing import Any, Dict, List, Optional, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

try:
    import shap
    _SHAP_OK = True
except ImportError:
    _SHAP_OK = False

ROOT        = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
MODEL_STORE = os.path.join(ROOT, "backend", "pragya_xai", "model_store")
OUTPUTS_DIR = os.path.join(ROOT, "backend", "pragya_xai", "outputs")

os.makedirs(OUTPUTS_DIR, exist_ok=True)


# ── SHAP computation ────────────────────────────────────────────────────────────

def _base_model(model: Any) -> Any:
    """Unwrap CalibratedClassifierCV to its base estimator."""
    if hasattr(model, "estimator"):
        return model.estimator
    if hasattr(model, "calibrated_classifiers_"):
        try:
            return model.calibrated_classifiers_[0].estimator
        except (AttributeError, IndexError):
            pass
    return model


def compute_shap_values(
    model: Any,
    X: pd.DataFrame,
) -> Optional[np.ndarray]:
    """
    Compute per-feature SHAP values for X (can be 1 or many rows).
    Returns ndarray shape (n_samples, n_features) or None on failure.
    """
    if not _SHAP_OK:
        return None

    base = _base_model(model)
    name = type(base).__name__

    try:
        if "Logistic" in name:
            exp   = shap.LinearExplainer(base, X)
            out   = exp(X)
            arr   = np.array(out.values)
        elif "Forest" in name or "XGB" in name or "Boost" in name:
            exp   = shap.TreeExplainer(base)
            raw   = exp.shap_values(X)
            if isinstance(raw, list) and len(raw) == 2:
                arr = np.array(raw[1])   # class-1 for RF
            else:
                arr = np.array(raw)
            if arr.ndim == 3:
                arr = arr[1]             # (n_classes, n_samples, n_features)
        else:
            exp = shap.Explainer(base, X)
            out = exp(X)
            arr = np.array(out.values)

        if arr.ndim == 1:
            arr = arr[np.newaxis, :]    # (1, n_features)
        return arr
    except Exception as exc:
        return None


# ── Plain-English translator ────────────────────────────────────────────────────

def translate_feature(name: str, value: Any, impact: float) -> str:
    """
    Convert (feature_name, raw_value, shap_impact) → plain English sentence
    for a non-technical government officer.

    Consistency guarantee:
        - impact > 0  => text must contain a "risk-increasing" phrase
        - impact < 0  => text must contain a "risk-reducing" phrase
    """
    up   = "raises risk"
    down = "lowers risk"
    dire = up if impact > 0 else down
    mag  = "significantly" if abs(impact) > 0.08 else "slightly"

    try:
        v = float(value)
    except (TypeError, ValueError):
        v = None

    # ── Feature-specific templates ──────────────────────────────────────────
    if name == "progress_gap":
        if v is None:
            return f"Progress data is unavailable, which {dire}."
        if v > 0:
            return (f"Progress is {v:.1f} points below the expected level, "
                    f"which {mag} {dire}.")
        if v < 0:
            return (f"Progress is {abs(v):.1f} points ahead of schedule, "
                    f"which {mag} {dire}.")
        return f"Progress is exactly on schedule, which {dire}."

    if name == "max_milestone_delay_months":
        if v is None or v == 0:
            return f"All milestones are on or ahead of schedule, which {dire}."
        return (f"A key milestone is {v:.1f} month(s) late, "
                f"which {mag} {dire}.")

    if name == "pct_milestones_delayed":
        if v is None:
            return f"Milestone data is unavailable, which {dire}."
        pct = round(v * 100, 1)
        if pct == 0:
            return f"No milestones are currently delayed, which {dire}."
        return (f"{pct:.1f}% of milestones are delayed, "
                f"which {mag} {dire}.")

    if name == "cost_growth_pct":
        if v is None:
            return f"Cost data unavailable, which {dire}."
        if v > 0:
            return (f"Cost growth is {v:.1f}% above the sanctioned amount, "
                    f"which {mag} {dire}.")
        if v < 0:
            return (f"Project is {abs(v):.1f}% under budget, "
                    f"which {mag} {dire}.")
        return f"Cost is exactly at the sanctioned amount, which {dire}."

    if name == "expenditure_to_progress_ratio":
        if v is None:
            return f"Expenditure ratio data unavailable, which {dire}."
        if v > 1.3:
            return (f"Money spent ({v:.2f}x) significantly exceeds physical progress, "
                    f"suggesting cost inefficiency, which {mag} {dire}.")
        if v > 1.0:
            return (f"Expenditure ratio ({v:.2f}x) is slightly above physical progress, "
                    f"which {dire}.")
        return (f"Expenditure ({v:.2f}x) is in line with physical progress, "
                f"which {dire}.")

    if name == "velocity_needed_to_finish":
        if v is None:
            return f"Required completion pace is unavailable, which {dire}."
        if v > 1.5:
            return (f"The project needs an unusually high pace ({v:.3f}%/day) to finish on time, "
                    f"which {mag} {dire}.")
        return (f"Required completion pace ({v:.3f}%/day) is manageable, "
                f"which {dire}.")

    if name in ("velocity_last_1", "velocity_last_3", "velocity_last_6"):
        period = name.split("_")[-1]
        label  = {"1": "last update", "3": "last 3 updates", "6": "last 6 updates"}[period]
        if v is None:
            return f"Progress velocity ({label}) is unavailable, which {dire}."
        if abs(v) < 0.001:
            return f"No progress was made in the {label}, which {mag} {dire}."
        if v < 0:
            return f"Progress regressed by {abs(v):.4f}%/day in the {label}, which {mag} {dire}."
        return f"Recent progress rate is {v:.4f}%/day ({label}), which {dire}."

    if name == "days_since_last_update":
        if v is None:
            return f"Update timing data unavailable, which {dire}."
        if v > 90:
            return (f"No update has been received in {int(v)} days (poor monitoring), "
                    f"which {mag} {dire}.")
        if v > 45:
            return (f"The last update was {int(v)} days ago, which {dire}.")
        return f"A recent update was received {int(v)} days ago, which {dire}."

    if name == "count_of_revised_dates":
        if v is None:
            return f"Revision count is unavailable, which {dire}."
        n = int(v)
        if n == 0:
            return f"No completion-date revisions recorded, which {dire}."
        return (f"The expected completion date has been revised {n} time(s), "
                f"which {mag} {dire}.")

    if name == "burn_rate_per_day":
        if v is None:
            return f"Daily burn rate unavailable, which {dire}."
        return f"Daily expenditure rate is Rs.{v:.2f} Cr/day, which {dire}."

    if name == "avg_update_gap":
        if v is None:
            return f"Update gap data unavailable, which {dire}."
        return f"Average gap between updates is {v:.0f} days, which {dire}."

    # Generic fallback
    clean = name.replace("_", " ").title()
    val_s = f"{v:.2f}" if v is not None else str(value)
    return f"{clean} is {val_s}, which {mag} {dire}."


def _consistency_enforce(text: str, impact: float) -> str:
    """Append a short tag if the text doesn't clearly signal risk direction."""
    has_up   = any(w in text.lower() for w in ["raises", "increases", "lowers" ,"reduces"])
    if not has_up:
        text += " [Increases Risk]" if impact > 0 else " [Reduces Risk]"
    return text


# ── Per-project bar chart ───────────────────────────────────────────────────────

def plot_shap_bar(
    contributions: List[Dict],
    project_id: str,
    target: str,
    risk_prob: float,
    save_path: Optional[str] = None,
) -> str:
    """
    Draw a horizontal SHAP bar chart for one project prediction.

    Returns base64-encoded PNG string (also saves to save_path if given).
    """
    n    = len(contributions)
    feats = [c["feature"].replace("_", " ").title() for c in contributions]
    vals  = [c["impact"] for c in contributions]
    colors= ["#E84040" if v > 0 else "#2ECC71" for v in vals]

    fig, ax = plt.subplots(figsize=(9, max(3, n * 0.65 + 1.5)))
    bars = ax.barh(feats[::-1], vals[::-1], color=colors[::-1], height=0.55, edgecolor="none")
    ax.axvline(0, color="#444", linewidth=0.8)

    # Labels on bars
    for bar, val in zip(bars, vals[::-1]):
        x_pos = val + (0.002 if val >= 0 else -0.002)
        align = "left" if val >= 0 else "right"
        ax.text(x_pos, bar.get_y() + bar.get_height() / 2,
                f"{val:+.3f}", va="center", ha=align, fontsize=8.5)

    risk_band = "High" if risk_prob > 0.6 else ("Medium" if risk_prob > 0.35 else "Low")
    band_color= {"High": "#E84040", "Medium": "#F39C12", "Low": "#27AE60"}[risk_band]
    title = (f"Project: {project_id}   |   {target.replace('label_', '').replace('_', ' ').title()}"
             f"\nRisk Score: {risk_prob:.1%}  [{risk_band}]")
    ax.set_title(title, fontsize=11, pad=10)
    ax.set_xlabel("SHAP Impact (red = increases risk, green = reduces risk)", fontsize=9)

    red_p  = mpatches.Patch(color="#E84040", label="Increases risk")
    grn_p  = mpatches.Patch(color="#2ECC71", label="Reduces risk")
    ax.legend(handles=[red_p, grn_p], loc="lower right", fontsize=8)
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150)
    plt.close(fig)
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode()

    if save_path:
        with open(save_path, "wb") as f:
            f.write(base64.b64decode(b64))

    return b64


# ── Global SHAP importance chart ────────────────────────────────────────────────

def plot_global_shap(
    model: Any,
    X_sample: pd.DataFrame,
    target: str,
    save_path: Optional[str] = None,
) -> Optional[str]:
    """
    Compute mean |SHAP| across X_sample and draw a ranked bar chart.
    Returns base64 PNG or None on failure.
    """
    arr = compute_shap_values(model, X_sample)
    if arr is None:
        return None

    mean_abs = np.abs(arr).mean(axis=0)
    feat_names = list(X_sample.columns)
    pairs = sorted(zip(feat_names, mean_abs), key=lambda x: x[1], reverse=True)[:15]
    names, vals = zip(*pairs)

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh(list(names)[::-1], list(vals)[::-1], color="#4C72B0", height=0.6)
    ax.set_xlabel("Mean |SHAP Value|", fontsize=10)
    ax.set_title(f"Global Feature Importance (SHAP) — {target}", fontsize=12)
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150)
    plt.close(fig)
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode()

    if save_path:
        with open(save_path, "wb") as f:
            f.write(base64.b64decode(b64))
    return b64


# ── Core explanation function ────────────────────────────────────────────────────

def get_top_shap_contributions(
    model: Any,
    X_row: pd.DataFrame,
    top_k: int = 5,
) -> List[Dict]:
    """
    Compute SHAP values for a single row and return top_k features
    with translated plain-English explanations.
    """
    arr = compute_shap_values(model, X_row)
    if arr is None:
        return [{"error": "SHAP computation failed (library missing or model unsupported)"}]

    shap_row  = arr[0]
    feat_vals = X_row.iloc[0].to_dict()
    feats     = list(X_row.columns)

    contribs = [
        {
            "feature": feat,
            "value":   feat_vals.get(feat),
            "impact":  float(shap_row[i]),
        }
        for i, feat in enumerate(feats)
        if i < len(shap_row)
    ]
    contribs.sort(key=lambda c: abs(c["impact"]), reverse=True)
    top = contribs[:top_k]

    for c in top:
        raw  = translate_feature(c["feature"], c["value"], c["impact"])
        c["explanation"] = _consistency_enforce(raw, c["impact"])

    return top


# ── Registry loader (singleton) ──────────────────────────────────────────────────

class _Registry:
    def __init__(self):
        self.models: Dict[str, Any]  = {}
        self.scaler                  = None
        self.cols: Dict              = {}
        self.selections: Dict[str, str] = {}
        self._loaded = False

    def load(self, store_dir: str = MODEL_STORE):
        if self._loaded:
            return
        for t in ("label_overrun", "label_delay"):
            p = os.path.join(store_dir, f"{t}_model.pkl")
            if os.path.exists(p):
                with open(p, "rb") as f:
                    self.models[t] = pickle.load(f)
        p = os.path.join(store_dir, "scaler.pkl")
        if os.path.exists(p):
            with open(p, "rb") as f:
                self.scaler = pickle.load(f)
        p = os.path.join(store_dir, "columns.json")
        if os.path.exists(p):
            with open(p) as f:
                self.cols = json.load(f)
        p = os.path.join(store_dir, "selections.json")
        if os.path.exists(p):
            with open(p) as f:
                self.selections = json.load(f)
        self._loaded = True

    def preprocess(self, feats: Dict) -> Tuple[pd.DataFrame, pd.DataFrame]:
        df = pd.DataFrame([feats])
        for col in NUMERIC_FEATURES:
            if col not in df.columns:
                df[col] = 0.0
        if self.scaler:
            num = [c for c in NUMERIC_FEATURES if c in df.columns]
            df[num] = self.scaler.transform(df[num].fillna(0))

        cats = [c for c in CATEGORICAL_FEATURES if c in df.columns]
        ohe  = pd.get_dummies(df, columns=cats, drop_first=False)
        if self.cols.get("ohe_cols"):
            ohe = ohe.reindex(columns=self.cols["ohe_cols"], fill_value=0)

        cat_df = df.copy()
        for c in CATEGORICAL_FEATURES:
            if c in cat_df.columns:
                cat_df[c] = cat_df[c].astype(str)
        if self.cols.get("cat_cols"):
            cat_df = cat_df.reindex(columns=self.cols["cat_cols"], fill_value=0)

        return ohe, cat_df


_REGISTRY = _Registry()

from backend.pragya_xai.features.pipeline import NUMERIC_FEATURES, CATEGORICAL_FEATURES


# ── Public API ────────────────────────────────────────────────────────────────────

def explain_risk(
    project_id: str,
    as_of_date: str,
    project_updates_df: pd.DataFrame,
    target: str = "label_overrun",
    top_k: int = 5,
    save_chart: bool = True,
) -> Dict[str, Any]:
    """
    The single public function the backend/dashboard calls.

    Parameters
    ----------
    project_id        : project identifier (for labelling charts)
    as_of_date        : 'YYYY-MM-DD'  — all data after this date is excluded
    project_updates_df: ALL update rows for the project (leakage guard inside)
    target            : 'label_overrun' or 'label_delay'
    top_k             : number of top SHAP features to return
    save_chart        : if True, saves PNG to outputs/

    Returns
    -------
    {
      project_id,
      as_of_date,
      target,
      risk_probability   : float  [0, 1]
      risk_band          : 'High' | 'Medium' | 'Low'
      top_reasons        : list[str]  — plain-English sentences
      shap_contributions : list[{feature, value, impact, explanation}]
      shap_chart         : base64-PNG string (embed in <img src="data:...">)
      chart_path         : absolute path to saved PNG (or None)
      model_version      : str
      feature_set_version: str
    }
    """
    from backend.pragya_xai.features.pipeline import compute_features

    _REGISTRY.load()

    # ── 1. Compute features ────────────────────────────────────────────────
    try:
        # Filter to as_of for leakage safety
        df_past = project_updates_df.copy()
        df_past["update_date"] = pd.to_datetime(df_past["update_date"])
        df_past = df_past[df_past["update_date"] <= pd.Timestamp(as_of_date)]
        feats = compute_features(df_past, as_of_date)
    except ValueError as exc:
        return {"error": str(exc)}

    if feats is None:
        return {"error": f"No data before {as_of_date}"}

    # ── 2. Preprocess ──────────────────────────────────────────────────────
    X_ohe, X_cat = _REGISTRY.preprocess(feats)

    if target not in _REGISTRY.models:
        return {"error": f"Model for '{target}' not found in model_store. Run training first."}

    model = _REGISTRY.models[target]
    is_catboost = "CatBoost" in type(_base_model(model)).__name__
    X = X_cat if is_catboost else X_ohe

    # ── 3. Predict ─────────────────────────────────────────────────────────
    try:
        risk_prob = float(model.predict_proba(X)[0, 1])
    except Exception as exc:
        return {"error": f"Prediction failed: {exc}"}

    risk_band = (
        "High"   if risk_prob > 0.60 else
        "Medium" if risk_prob > 0.35 else
        "Low"
    )

    # ── 4. SHAP ────────────────────────────────────────────────────────────
    contribs = get_top_shap_contributions(model, X, top_k=top_k)
    top_reasons = [c["explanation"] for c in contribs if "explanation" in c]

    # ── 5. Chart ───────────────────────────────────────────────────────────
    chart_b64  = ""
    chart_path = None
    if contribs and "error" not in contribs[0]:
        fname = f"{project_id}_{target}_{as_of_date.replace('-', '')}.png"
        chart_path = os.path.join(OUTPUTS_DIR, fname) if save_chart else None
        chart_b64  = plot_shap_bar(contribs, project_id, target, risk_prob, save_path=chart_path)

    return {
        "project_id":          project_id,
        "as_of_date":          as_of_date,
        "target":              target,
        "risk_probability":    round(risk_prob, 4),
        "risk_band":           risk_band,
        "top_reasons":         top_reasons,
        "shap_contributions":  contribs,
        "shap_chart":          chart_b64,
        "chart_path":          chart_path,
        "model_version":       "1.0.0",
        "feature_set_version": _REGISTRY.cols.get("feature_set_version", "xai_v1.0"),
    }
