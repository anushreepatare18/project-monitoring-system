import shap
import numpy as np

def explain_prediction(model, X_instance, model_name="CatBoost"):
    """
    Computes SHAP values for a single prediction and returns top-5 features.
    X_instance: 1-row DataFrame with named columns.
    """
    import numpy as np

    # ── 1. Compute raw SHAP values ─────────────────────────────────────────
    if model_name == "LogisticRegression":
        # CalibratedClassifierCV wrapping a LogisticRegression
        base = model.estimator if hasattr(model, 'estimator') else model
        explainer = shap.Explainer(base, X_instance)
        shap_out  = explainer(X_instance)
    elif model_name in ("RandomForest", "XGBoost"):
        base = model.estimator if hasattr(model, 'estimator') else model
        try:
            explainer = shap.TreeExplainer(base)
            shap_out  = explainer.shap_values(X_instance)
        except Exception:
            explainer = shap.Explainer(model, X_instance)
            shap_out  = explainer(X_instance)
    else:  # CatBoost (or any direct tree model)
        explainer = shap.TreeExplainer(model)
        shap_out  = explainer.shap_values(X_instance)

    # ── 2. Normalise to a flat 1-D array of per-feature contributions ─────
    # SHAP can return various shapes:
    #   • shap.Explanation object          → .values shape (n_samples, n_features)
    #   • list of arrays (multi-class RF)  → pick class-1 array
    #   • 3D array (n_classes, n_samples, n_features)  → pick class-1
    #   • 2D array (n_samples, n_features)
    #   • 1D array (n_features)
    if hasattr(shap_out, 'values'):
        arr = np.array(shap_out.values)
    else:
        arr = np.array(shap_out)

    if isinstance(shap_out, list):
        # Multi-output list: take class-1 slice
        arr = np.array(shap_out[1])

    # Squeeze to 2-D (n_samples, n_features)
    if arr.ndim == 3:          # (n_classes, n_samples, n_features)
        arr = arr[1]           # class-1
    if arr.ndim == 1:          # already (n_features,)
        vals = arr
    else:                      # (n_samples, n_features)
        vals = arr[0]

    # ── 3. Pair with feature names ────────────────────────────────────────
    features     = list(X_instance.columns)
    feature_vals = X_instance.iloc[0].to_dict()

    contributions = [
        {
            'feature': feature,
            'value':   feature_vals[feature],
            'impact':  float(vals[i]),
        }
        for i, feature in enumerate(features)
        if i < len(vals)  # guard against length mismatch
    ]

    # Sort by absolute impact descending
    contributions.sort(key=lambda x: abs(x['impact']), reverse=True)
    top_5 = contributions[:5]

    # ── 4. Add plain-English explanation ─────────────────────────────────
    for c in top_5:
        c['explanation'] = translate_feature(c['feature'], c['value'], c['impact'])

        # Consistency enforcement
        if c['impact'] > 0 and 'increases risk' not in c['explanation'].lower() and 'raises' not in c['explanation'].lower():
            c['explanation'] += " (Increases Risk)"
        elif c['impact'] < 0 and 'decreases risk' not in c['explanation'].lower() and 'lowers' not in c['explanation'].lower():
            c['explanation'] += " (Decreases Risk)"

    return top_5

def translate_feature(feature_name, feature_value, impact):
    direction = "increases risk" if impact > 0 else "decreases risk"
    mag = "significantly" if abs(impact) > 0.1 else "slightly"
    
    if feature_name == 'progress_gap':
        val = round(feature_value, 1)
        if val > 0:
            return f"Progress is {val}% below the expected planned level, which {mag} {direction}."
        else:
            return f"Progress is {-val}% ahead of the expected planned level, which {mag} {direction}."
            
    elif feature_name == 'max_milestone_delay_months':
        val = round(feature_value, 1)
        if val > 0:
            return f"A key milestone is {val} months late, which {mag} {direction}."
        else:
            return f"Milestones are generally on track, which {direction}."
            
    elif feature_name == 'cost_growth_pct':
        val = round(feature_value, 1)
        if val > 0:
            return f"Cost growth is {val}% over the sanctioned budget, which {mag} {direction}."
        else:
            return f"Project is operating within budget, which {direction}."
            
    elif feature_name == 'velocity_needed_to_finish':
        val = round(feature_value, 2)
        if val > 1.0:
            return f"The required pace of {val}% per day is unusually high, which {direction}."
        else:
            return f"The required pace to finish is manageable at {val}% per day, which {direction}."
            
    elif feature_name == 'pct_milestones_delayed':
        val = round(feature_value * 100, 1)
        if val > 0:
            return f"{val}% of milestones are delayed, which {mag} {direction}."
        else:
            return f"No major milestones are delayed, which {direction}."
            
    elif feature_name == 'expenditure_to_progress_ratio':
        val = round(feature_value, 2)
        if val > 1.2:
            return f"Expenditure ratio ({val}x) exceeds physical progress significantly, which {direction}."
        else:
            return f"Expenditure is in line with physical progress ({val}x), which {direction}."
            
    elif feature_name == 'days_since_last_update':
        val = round(feature_value, 0)
        if val > 60:
            return f"It has been {val} days since the last update, indicating poor tracking, which {direction}."
        else:
            return f"Recent update received ({val} days ago), which {direction}."
            
    # Generic fallback
    clean_name = feature_name.replace('_', ' ').capitalize()
    return f"{clean_name} has a value of {round(feature_value, 2) if isinstance(feature_value, float) else feature_value}, which {direction}."
