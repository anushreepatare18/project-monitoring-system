"""
PRAGYA AI — Explainability Layer (Task 5)

Provides:
  - SHAP value computation for tree/linear models
  - Plain-language officer-facing explanation translator
  - Consistency check enforcement
  - Global summary generation
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False


# ── Plain-language translation ────────────────────────────────────────────────

def translate_feature(
    feature_name: str,
    feature_value: Any,
    impact: float,
) -> str:
    """
    Convert a (feature_name, value, shap_impact) triple into an officer-
    facing English sentence. Impact > 0 increases risk; < 0 decreases risk.
    """
    direction = "increases" if impact > 0 else "lowers"
    magnitude = "significantly" if abs(impact) > 0.08 else "slightly"

    try:
        val = float(feature_value)
    except (TypeError, ValueError):
        val = None

    # ── Per-feature translation table ────────────────────────────────────────
    if feature_name == "progress_gap":
        if val is None:
            return f"Progress gap data is unavailable, which {direction} risk."
        v = round(val, 1)
        if v > 0:
            return (
                f"Progress is {v:.1f} points behind the expected schedule level, "
                f"which {magnitude} {direction} risk."
            )
        elif v < 0:
            return (
                f"Progress is {abs(v):.1f} points ahead of the expected schedule level, "
                f"which {magnitude} {direction} risk."
            )
        return f"Progress is exactly on schedule, which {direction} risk."

    elif feature_name == "max_milestone_delay_months":
        if val is None or val == 0:
            return f"All tracked milestones are on or ahead of schedule, which {direction} risk."
        return (
            f"The most delayed milestone is {val:.1f} month(s) late, "
            f"which {magnitude} {direction} risk."
        )

    elif feature_name == "pct_milestones_delayed":
        if val is None:
            return f"Milestone tracking data is unavailable, which {direction} risk."
        pct = round(val * 100, 1)
        if pct == 0:
            return f"No milestones are currently delayed, which {direction} risk."
        return (
            f"{pct:.1f}% of tracked milestones are delayed, "
            f"which {magnitude} {direction} risk."
        )

    elif feature_name == "cost_growth_pct":
        if val is None:
            return f"Cost data is unavailable, which {direction} risk."
        v = round(val, 1)
        if v > 0:
            return (
                f"Revised cost is {v:.1f}% above the sanctioned budget, "
                f"which {magnitude} {direction} risk."
            )
        elif v < 0:
            return (
                f"Project is operating {abs(v):.1f}% below the sanctioned budget, "
                f"which {magnitude} {direction} risk."
            )
        return f"Revised cost matches the sanctioned budget, which {direction} risk."

    elif feature_name == "expenditure_to_progress_ratio":
        if val is None:
            return f"Expenditure-to-progress data is unavailable."
        v = round(val, 2)
        if v > 1.3:
            return (
                f"Money spent ({v:.2f}x) is significantly ahead of physical progress, "
                f"suggesting cost inefficiency, which {magnitude} {direction} risk."
            )
        elif v > 1.0:
            return (
                f"Expenditure ratio ({v:.2f}x) is slightly above physical progress, "
                f"which {direction} risk."
            )
        return (
            f"Expenditure is in line with physical progress ({v:.2f}x), "
            f"which {direction} risk."
        )

    elif feature_name == "velocity_needed_to_finish":
        if val is None:
            return f"Completion velocity data is unavailable."
        v = round(val, 3)
        if v > 1.5:
            return (
                f"The project needs to progress at {v:.3f}% per day to finish on time — "
                f"an unusually high rate, which {magnitude} {direction} risk."
            )
        elif v > 0.5:
            return (
                f"Required pace ({v:.3f}% per day) is achievable but demanding, "
                f"which {direction} risk."
            )
        return (
            f"Required completion pace ({v:.3f}% per day) is manageable, "
            f"which {direction} risk."
        )

    elif feature_name == "velocity_last_1":
        if val is None:
            return f"Recent progress velocity data is unavailable."
        v = round(val, 4)
        if abs(v) < 0.001:
            return f"No physical progress was recorded in the most recent update, which {magnitude} {direction} risk."
        if v < 0:
            return f"Physical progress regressed by {abs(v):.4f}% per day in the last update, which {magnitude} {direction} risk."
        return f"Recent progress rate is {v:.4f}% per day, which {direction} risk."

    elif feature_name == "days_since_last_update":
        if val is None:
            return f"Update frequency data is unavailable."
        v = round(val, 0)
        if v > 90:
            return (
                f"No update has been received in {int(v)} days, "
                f"indicating poor monitoring, which {magnitude} {direction} risk."
            )
        elif v > 45:
            return (
                f"The last update was {int(v)} days ago, "
                f"which {direction} risk."
            )
        return f"A recent update was received {int(v)} days ago, which {direction} risk."

    elif feature_name == "burn_rate_per_day":
        if val is None:
            return f"Burn rate data is unavailable."
        v = round(val, 2)
        return f"Daily expenditure rate is ₹{v:.2f} Cr/day, which {direction} risk."

    elif feature_name == "count_of_revised_dates":
        if val is None:
            return f"Revision count data is unavailable."
        v = int(val)
        if v == 0:
            return f"No completion date revisions have been recorded, which {direction} risk."
        return (
            f"The expected completion date has been revised {v} time(s), "
            f"which {magnitude} {direction} risk."
        )

    elif feature_name == "avg_update_gap":
        if val is None:
            return f"Update gap data is unavailable."
        v = round(val, 1)
        return (
            f"Average gap between project updates is {v:.1f} days, "
            f"which {direction} risk."
        )

    # ── Generic fallback ──────────────────────────────────────────────────────
    clean = feature_name.replace("_", " ").title()
    val_display = f"{val:.2f}" if isinstance(val, float) else str(feature_value)
    return (
        f"{clean} has a value of {val_display}, "
        f"which {magnitude} {direction} risk."
    )


def _consistency_check(explanation: str, impact: float) -> str:
    """
    Enforce that the text actually says 'increases' or 'lowers' risk
    consistently with the sign of the SHAP impact.
    """
    is_positive = impact > 0
    mentions_increase = any(w in explanation.lower() for w in ["increases", "raises", "significant"])
    mentions_decrease = any(w in explanation.lower() for w in ["lowers", "decreases", "below"])

    if is_positive and not mentions_increase and not mentions_decrease:
        explanation += " [↑ Increases Risk]"
    elif not is_positive and not mentions_decrease and not mentions_increase:
        explanation += " [↓ Lowers Risk]"

    return explanation


# ── SHAP computation ──────────────────────────────────────────────────────────

def explain_prediction(
    model: Any,
    X_instance: pd.DataFrame,
    model_name: str = "CatBoost",
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """
    Compute SHAP values for a single prediction and return top-k features
    with plain-language explanations.

    Parameters
    ----------
    model : fitted sklearn/catboost/xgboost model or CalibratedClassifierCV
    X_instance : pd.DataFrame with exactly 1 row
    model_name : one of 'LogisticRegression', 'RandomForest', 'XGBoost', 'CatBoost'
    top_k : how many top features to return (default 5)

    Returns
    -------
    list of dicts: [{feature, value, impact, explanation}, ...]
    """
    if not SHAP_AVAILABLE:
        return [{"error": "shap library not installed. Run: pip install shap"}]

    if X_instance.empty:
        return [{"error": "Empty input — cannot compute SHAP."}]

    # ── Resolve base estimator if wrapped by CalibratedClassifierCV ──────────
    base_model = model
    if hasattr(model, "estimator"):
        base_model = model.estimator
    elif hasattr(model, "calibrated_classifiers_"):
        # Multi-fold calibration: use first base estimator
        try:
            base_model = model.calibrated_classifiers_[0].estimator
        except (AttributeError, IndexError):
            base_model = model

    resolved_name = type(base_model).__name__

    # ── Compute raw SHAP values ───────────────────────────────────────────────
    shap_vals: Optional[np.ndarray] = None

    try:
        if "Logistic" in resolved_name or "linear" in resolved_name.lower():
            explainer = shap.LinearExplainer(base_model, X_instance)
            shap_out  = explainer(X_instance)
            arr       = np.array(shap_out.values)

        elif "Forest" in resolved_name or "XGB" in resolved_name or "Boost" in resolved_name:
            explainer = shap.TreeExplainer(base_model)
            raw       = explainer.shap_values(X_instance)
            # RF returns list of 2 arrays [class0, class1]
            if isinstance(raw, list) and len(raw) == 2:
                arr = np.array(raw[1])
            else:
                arr = np.array(raw)

        else:
            # Generic fallback (Kernel explainer — slow but universal)
            explainer = shap.Explainer(base_model, X_instance)
            shap_out  = explainer(X_instance)
            arr       = np.array(shap_out.values)

        # Normalise to 1-D
        if arr.ndim == 3:
            arr = arr[1]  # (n_classes, n_samples, n_features) → class-1
        if arr.ndim == 2:
            arr = arr[0]  # (n_samples, n_features) → first sample

        shap_vals = arr

    except Exception as exc:
        return [{"error": f"SHAP computation failed: {exc}"}]

    # ── Pair with feature names ───────────────────────────────────────────────
    features     = list(X_instance.columns)
    feature_vals = X_instance.iloc[0].to_dict()

    contributions = []
    for i, feat in enumerate(features):
        if i >= len(shap_vals):
            break
        contributions.append({
            "feature": feat,
            "value":   feature_vals.get(feat),
            "impact":  float(shap_vals[i]),
        })

    contributions.sort(key=lambda x: abs(x["impact"]), reverse=True)
    top = contributions[:top_k]

    # ── Add translations + consistency check ─────────────────────────────────
    for c in top:
        raw_text = translate_feature(c["feature"], c["value"], c["impact"])
        c["explanation"] = _consistency_check(raw_text, c["impact"])

    return top


# ── Global SHAP summary ───────────────────────────────────────────────────────

def compute_global_shap_summary(
    model: Any,
    X_test: pd.DataFrame,
    model_name: str = "CatBoost",
    sample_size: int = 500,
) -> Dict[str, float]:
    """
    Compute mean |SHAP value| per feature across a test sample.
    Used for model debugging and sector-level global summaries.

    Returns
    -------
    dict mapping feature_name → mean_abs_shap  (sorted descending)
    """
    if not SHAP_AVAILABLE:
        return {}

    if len(X_test) > sample_size:
        X_sample = X_test.sample(sample_size, random_state=42)
    else:
        X_sample = X_test.copy()

    base_model = model
    if hasattr(model, "estimator"):
        base_model = model.estimator
    elif hasattr(model, "calibrated_classifiers_"):
        try:
            base_model = model.calibrated_classifiers_[0].estimator
        except (AttributeError, IndexError):
            pass

    resolved_name = type(base_model).__name__

    try:
        if "Logistic" in resolved_name:
            explainer  = shap.LinearExplainer(base_model, X_sample)
            shap_vals  = explainer(X_sample).values
        else:
            explainer = shap.TreeExplainer(base_model)
            raw       = explainer.shap_values(X_sample)
            if isinstance(raw, list) and len(raw) == 2:
                shap_vals = np.array(raw[1])
            else:
                shap_vals = np.array(raw)

        if shap_vals.ndim == 3:
            shap_vals = shap_vals[1]

        mean_abs = np.abs(shap_vals).mean(axis=0)
        summary  = {
            feat: float(round(mean_abs[i], 6))
            for i, feat in enumerate(X_sample.columns)
            if i < len(mean_abs)
        }
        return dict(sorted(summary.items(), key=lambda x: x[1], reverse=True))

    except Exception as exc:
        return {"error": str(exc)}
