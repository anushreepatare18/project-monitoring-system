"""
PRAGYA AI — SHAP Explainer & Plain-Language Translator  (v2)
=============================================================
Responsibilities:
  1. Compute SHAP values for any supported model type
     (TreeExplainer for tree models, LinearExplainer for LR)
  2. Extract top-5 contributing features (sign + magnitude)
  3. Translate technical feature names + values into plain-English
     officer-facing sentences (with a consistency check)
  4. Generate a per-project bar chart
  5. Generate a global feature-importance summary chart
"""
from __future__ import annotations

import os
import warnings
from pathlib import Path
from typing import Any, Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap

warnings.filterwarnings("ignore")

CHART_DIR = Path("ml_core/registry")
CHART_DIR.mkdir(parents=True, exist_ok=True)


# ── Plain-language translation layer ─────────────────────────────────────────

def translate_to_plain_language(
    feature_name: str,
    feature_val: Any,
    shap_val: float,
) -> str:
    """
    Convert a raw feature (name, value, SHAP contribution) into a sentence
    a government officer can understand.

    Consistency contract (enforced by caller):
      - The numeric in the sentence must equal `feature_val` (not recomputed).
      - The direction word ("increases"/"decreases") must match sign(shap_val).
    """
    direction = "increases" if shap_val > 0 else "decreases"

    # Normalise feature name (remove sklearn transformer prefixes)
    feat = (
        feature_name
        .replace("num__", "")
        .replace("cat__", "")
    )

    try:
        val = round(float(feature_val), 2)
    except (TypeError, ValueError):
        val = feature_val

    if "progress_gap" in feat:
        side = "below" if val > 0 else "above"
        return (
            f"Progress is {abs(val):.1f}% {side} the expected level at this stage, "
            f"which {direction} risk."
        )
    if "max_milestone_delay_months" in feat:
        return (
            f"A key milestone is delayed by {val:.1f} months, "
            f"which {direction} risk."
        )
    if "pct_milestones_delayed" in feat:
        pct = int(round(val * 100))
        return (
            f"{pct}% of tracked milestones are currently delayed, "
            f"which {direction} risk."
        )
    if "cost_growth_pct" in feat:
        return (
            f"Revised cost has grown {val:.1f}% above the sanctioned budget, "
            f"which {direction} risk."
        )
    if "expenditure_to_progress_ratio" in feat:
        return (
            f"Expenditure-to-progress ratio is {val:.2f} "
            f"(1.0 = on-track spending), "
            f"which {direction} risk."
        )
    if "burn_rate" in feat:
        return (
            f"Burn rate (spend vs. time elapsed) is {val:.2f}x expected, "
            f"which {direction} risk."
        )
    if "velocity_needed_to_finish" in feat:
        return (
            f"To finish on time the project needs {val:.3f}% daily progress — "
            f"substantially higher than current velocity, "
            f"which {direction} risk."
        )
    if "progress_velocity_1" in feat:
        return (
            f"Progress gained in the last update was {val:.1f} percentage points, "
            f"which {direction} risk."
        )
    if "progress_velocity_3" in feat:
        return (
            f"Average progress over the last 3 updates is {val:.2f}%/update, "
            f"which {direction} risk."
        )
    if "count_of_revised_dates" in feat:
        return (
            f"The expected completion date has been revised {int(val)} time(s), "
            f"which {direction} risk."
        )
    if "days_since_last_update" in feat:
        return (
            f"The last update was {int(val)} days ago "
            f"(higher gaps may mean stalled reporting), "
            f"which {direction} risk."
        )
    if "avg_update_gap" in feat:
        return (
            f"The average reporting gap across all updates is {val:.0f} days, "
            f"which {direction} risk."
        )
    if "missing_velocity_flag" in feat:
        present = "is" if val else "is not"
        return (
            f"The velocity indicator {present} missing (first or only update), "
            f"which {direction} risk."
        )
    # Categorical features (one-hot encoded)
    if "sector" in feat or "ministry" in feat or "agency" in feat or "state" in feat:
        category_val = feat.split("_")[-1] if "_" in feat else str(val)
        return (
            f"Project category '{category_val}' is a factor, "
            f"which {direction} risk."
        )
    # Fallback
    return (
        f"Feature '{feat}' with value {val} {direction} risk."
    )


def _check_consistency(feature_val: float, text: str, feature_name: str) -> None:
    """
    Soft consistency check: verify the number in the text matches feature_val.
    Raises ValueError on a clear contradiction.
    """
    try:
        val_rounded = round(float(feature_val), 1)
    except (TypeError, ValueError):
        return  # categorical value, skip numeric check
    val_str = str(abs(val_rounded))
    # We only check non-zero numeric features
    if val_rounded != 0.0 and val_str not in text and str(int(abs(val_rounded))) not in text:
        raise ValueError(
            f"Consistency error for '{feature_name}': "
            f"feature_val={feature_val} not found in text: '{text}'"
        )


# ── SHAP computation ──────────────────────────────────────────────────────────

def _get_base_clf_and_X(model, X_sample):
    """Unwrap CalibratedWrapper/Pipeline to get raw clf + transformed X."""
    # Unwrap our CalibratedWrapper
    if hasattr(model, '_base'):
        model = model._base
    # Unwrap sklearn CalibratedClassifierCV
    if hasattr(model, 'calibrated_classifiers_'):
        model = model.estimator
    if hasattr(model, 'named_steps'):
        clf  = model.named_steps["clf"]
        prep = model.named_steps["prep"]
        X_tr = prep.transform(X_sample)
        try:
            feat_names = list(prep.get_feature_names_out())
        except Exception:
            feat_names = [f"f{i}" for i in range(X_tr.shape[1])]
        if not hasattr(X_tr, 'iloc'):
            import pandas as pd
            X_tr = pd.DataFrame(X_tr, columns=feat_names)
    else:
        clf        = model
        X_tr       = X_sample
        feat_names = list(X_sample.columns)
    return clf, X_tr, feat_names


def explain_prediction(
    model: Any,
    X_sample: pd.DataFrame,
    model_name: str,
    project_id: str = "unknown",
    save_chart: bool = True,
) -> tuple[list[dict], Optional[str]]:
    """
    Compute SHAP values for a single sample and return the top-5 explanations.

    Returns
    -------
    explanations : list[dict]
        Each dict has keys: feature, shap_value, feature_value, text
    chart_path : str or None
        Path to the saved bar chart (None if save failed).
    """
    try:
        clf, X_tr, feat_names = _get_base_clf_and_X(model, X_sample)
    except Exception as e:
        print(f"[shap] Pre-processing error: {e}. Returning fallback.")
        return _fallback_explanation(), None

    try:
        clf_type = type(clf).__name__
        if clf_type in ("RandomForestClassifier", "XGBClassifier", "CatBoostClassifier"):
            explainer   = shap.TreeExplainer(clf)
            shap_vals   = explainer.shap_values(X_tr)
            if isinstance(shap_vals, list):       # binary: [neg_class, pos_class]
                shap_vals = shap_vals[1]
        elif clf_type == "LogisticRegression":
            explainer   = shap.LinearExplainer(clf, X_tr, feature_perturbation="interventional")
            shap_vals   = explainer.shap_values(X_tr)
        else:
            explainer   = shap.Explainer(clf, X_tr)
            shap_vals   = explainer(X_tr).values
            if shap_vals.ndim == 3:
                shap_vals = shap_vals[:, :, 1]

        sv_row = shap_vals[0]   # first (and only) sample
        fv_row = X_tr.iloc[0].values if hasattr(X_tr, "iloc") else X_tr[0]

        df_shap = pd.DataFrame({
            "feature":       feat_names,
            "shap_value":    sv_row,
            "feature_value": fv_row,
            "abs_shap":      np.abs(sv_row),
        })
        top5 = df_shap.sort_values("abs_shap", ascending=False).head(5)

        explanations: list[dict] = []
        for _, row in top5.iterrows():
            text = translate_to_plain_language(
                row["feature"], row["feature_value"], row["shap_value"]
            )
            # Consistency check (soft)
            try:
                _check_consistency(row["feature_value"], text, row["feature"])
            except ValueError as ce:
                print(f"[shap] Consistency warning: {ce}")

            explanations.append({
                "feature":       row["feature"],
                "shap_value":    float(row["shap_value"]),
                "feature_value": (
                    float(row["feature_value"])
                    if isinstance(row["feature_value"], (int, float, np.floating))
                    else row["feature_value"]
                ),
                "text": text,
            })

        chart_path = None
        if save_chart:
            chart_path = _save_local_bar_chart(
                list(top5["feature"]),
                list(top5["shap_value"]),
                model_name,
                project_id,
            )

        return explanations, chart_path

    except Exception as e:
        print(f"[shap] Explainer error: {e}. Returning fallback.")
        return _fallback_explanation(), None


def explain_global(
    model: Any,
    X_background: pd.DataFrame,
    model_name: str,
    target: str,
    n_samples: int = 200,
) -> Optional[str]:
    """
    Compute mean |SHAP value| per feature over a background sample.
    Saves a global importance bar chart and returns the path.
    """
    try:
        clf, X_tr, feat_names = _get_base_clf_and_X(model, X_background.head(n_samples))
        clf_type = type(clf).__name__

        if clf_type in ("RandomForestClassifier", "XGBClassifier", "CatBoostClassifier"):
            explainer = shap.TreeExplainer(clf)
            sv        = explainer.shap_values(X_tr)
            if isinstance(sv, list):
                sv = sv[1]
        elif clf_type == "LogisticRegression":
            explainer = shap.LinearExplainer(clf, X_tr, feature_perturbation="interventional")
            sv        = explainer.shap_values(X_tr)
        else:
            explainer = shap.Explainer(clf, X_tr)
            sv        = explainer(X_tr).values
            if sv.ndim == 3:
                sv = sv[:, :, 1]

        mean_abs = np.abs(sv).mean(axis=0)
        idx_sort = np.argsort(mean_abs)[::-1][:15]   # top 15
        top_feats = [feat_names[i] for i in idx_sort]
        top_vals  = [mean_abs[i]   for i in idx_sort]

        path = str(CHART_DIR / f"{target}_{model_name}_global_shap.png")
        fig, ax = plt.subplots(figsize=(9, 6))
        ax.barh(top_feats[::-1], top_vals[::-1], color="#6366f1")
        ax.set_xlabel("Mean |SHAP Value|")
        ax.set_title(
            f"Global Feature Importance — {model_name} ({target})\n"
            f"(mean |SHAP| over {min(n_samples, len(X_background))} samples)"
        )
        fig.tight_layout()
        fig.savefig(path, dpi=100)
        plt.close(fig)
        print(f"[shap] Global chart saved → {path}")
        return path

    except Exception as e:
        print(f"[shap] Global explainer error: {e}")
        return None


# ── Chart helpers ─────────────────────────────────────────────────────────────

def _save_local_bar_chart(
    features: list[str],
    shap_values: list[float],
    model_name: str,
    project_id: str,
) -> str:
    safe_pid = project_id.replace("/", "-").replace(" ", "_")
    path = str(CHART_DIR / f"shap_{safe_pid}_{model_name}.png")
    CHART_DIR.mkdir(parents=True, exist_ok=True)

    colors = ["#ef4444" if v > 0 else "#10b981" for v in shap_values]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(features[::-1], shap_values[::-1], color=colors[::-1])
    ax.axvline(0, color="black", linewidth=0.8, linestyle="--")
    ax.set_xlabel("SHAP Value (positive = increases risk)")
    ax.set_title(f"Top Feature Contributions — Project {project_id}")
    fig.tight_layout()
    fig.savefig(path, dpi=100)
    plt.close(fig)
    return path


def _fallback_explanation() -> list[dict]:
    """Return a clearly-labelled fallback when SHAP computation fails."""
    return [
        {
            "feature":       "progress_gap",
            "shap_value":    0.15,
            "feature_value": 12.0,
            "text": (
                "Progress is 12.0% below the expected level at this stage, "
                "which increases risk. [Note: SHAP computation unavailable; "
                "this is a placeholder.]"
            ),
        }
    ]
