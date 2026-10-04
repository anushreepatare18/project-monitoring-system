"""Patch shap_explainer.py to handle CalibratedWrapper."""
import re

path = "ml_core/explain/shap_explainer.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Check if function already there
if "_get_base_clf_and_X" in content:
    # Find and replace the function body
    pattern = re.compile(
        r'(# .*?SHAP computation.*?\n\n)def _get_base_clf_and_X.*?return clf, X_tr, feat_names',
        re.DOTALL
    )
    replacement = r'''\1def _get_base_clf_and_X(model, X_sample):
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
    return clf, X_tr, feat_names'''
    new_content = pattern.sub(replacement, content)
    if new_content == content:
        print("Regex did not match — injecting at SHAP computation marker")
        marker = "# ── SHAP computation"
        if marker not in new_content:
            marker = "# -- SHAP computation"
        # Just prepend function before explain_prediction
        func_code = '''

def _get_base_clf_and_X(model, X_sample):
    """Unwrap CalibratedWrapper/Pipeline to get raw clf + transformed X."""
    if hasattr(model, '_base'):
        model = model._base
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
        import pandas as pd
        if not hasattr(X_tr, 'iloc'):
            X_tr = pd.DataFrame(X_tr, columns=feat_names)
    else:
        clf        = model
        X_tr       = X_sample
        feat_names = list(X_sample.columns)
    return clf, X_tr, feat_names

'''
        idx = new_content.find("def explain_prediction(")
        new_content = new_content[:idx] + func_code + new_content[idx:]
else:
    print("Function not found, injecting fresh")
    func_code = '''

def _get_base_clf_and_X(model, X_sample):
    """Unwrap CalibratedWrapper/Pipeline to get raw clf + transformed X."""
    if hasattr(model, '_base'):
        model = model._base
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
        import pandas as pd
        if not hasattr(X_tr, 'iloc'):
            X_tr = pd.DataFrame(X_tr, columns=feat_names)
    else:
        clf        = model
        X_tr       = X_sample
        feat_names = list(X_sample.columns)
    return clf, X_tr, feat_names

'''
    new_content = content
    idx = new_content.find("def explain_prediction(")
    new_content = new_content[:idx] + func_code + new_content[idx:]

with open(path, "w", encoding="utf-8") as f:
    f.write(new_content)

print("Done. Function present:", "_get_base_clf_and_X" in new_content)
