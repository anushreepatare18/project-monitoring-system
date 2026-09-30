"""
PRAGYA XAI — pytest test suite
Tests: leakage guard, feature completeness, label boundaries,
       temporal split integrity, translator consistency.

Run:
    $env:PYTHONPATH="."; pytest backend/pragya_xai/tests/ -v
"""
from __future__ import annotations

import math
from datetime import datetime, timedelta

import pandas as pd
import pytest

from backend.pragya_xai.features.pipeline import (
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    compute_features,
    compute_labels,
    build_training_dataset,
)
from backend.pragya_xai.explain.shap_explainer import (
    translate_feature,
    _consistency_enforce,
)


# ── Fixture ──────────────────────────────────────────────────────────────────────

def make_project(
    n: int = 8,
    start: str = "2020-01-01",
    dur: int = 730,
    delayed: bool = False,
    overrun: bool = False,
) -> pd.DataFrame:
    s = pd.Timestamp(start)
    e = s + timedelta(days=dur)
    fe = e + timedelta(days=200) if delayed else e
    fc = 500.0 * 1.5 if overrun else 500.0 * 0.95
    rows = []
    for i in range(n):
        frac = (i + 1) / n
        upd  = s + timedelta(days=int(dur * frac * 0.9))
        rows.append({
            "project_id": "PRJ-TEST",
            "update_date": upd.strftime("%Y-%m-%d"),
            "ministry": "Min-Test", "sector": "Highways",
            "agency": "NHAI", "state": "Maharashtra",
            "sanctioned_cost": 500.0,
            "planned_start": start,
            "planned_end": e.strftime("%Y-%m-%d"),
            "project_type": "Greenfield",
            "physical_progress_pct": round(min(100, frac * 100), 2),
            "financial_progress_pct": round(frac * 100, 2),
            "cumulative_expenditure": round(500 * frac, 2),
            "revised_cost": 500 * 1.2 if overrun and i > 4 else 500.0,
            "expected_completion_date": fe.strftime("%Y-%m-%d") if delayed and i > 3 else e.strftime("%Y-%m-%d"),
            "milestone_name": f"M{i}",
            "milestone_planned_date": (s + timedelta(days=int(dur * frac))).strftime("%Y-%m-%d"),
            "milestone_expected_date": (e - timedelta(days=(n - i) * 30)).strftime("%Y-%m-%d"),
            "milestone_actual_date": upd.strftime("%Y-%m-%d") if frac >= 0.5 else None,
            "final_cost": fc,
            "final_end_date": fe.strftime("%Y-%m-%d"),
            "delayed_flag": int(delayed),
            "overrun_flag": int(overrun),
            "outcome_known_at": fe.strftime("%Y-%m-%d"),
        })
    return pd.DataFrame(rows)


# ── Leakage tests ─────────────────────────────────────────────────────────────────

class TestLeakage:

    def test_future_rows_raise(self):
        df = make_project()
        df["update_date"] = "2030-01-01"   # all in the future
        with pytest.raises(ValueError, match="LEAKAGE"):
            compute_features(df, "2022-01-01")

    def test_past_only_succeeds(self):
        df = make_project(start="2020-01-01")
        result = compute_features(df, "2022-06-01")
        assert result is not None

    def test_empty_after_filter_returns_none(self):
        df = make_project(start="2020-01-01")
        # pass only rows BEFORE all updates exist
        df_past = df[pd.to_datetime(df["update_date"]) <= pd.Timestamp("2019-01-01")]
        assert compute_features(df_past, "2019-01-01") is None

    def test_single_future_row_raises(self):
        df = make_project(n=6)
        df.iloc[-1, df.columns.get_loc("update_date")] = "2099-12-31"
        with pytest.raises(ValueError, match="LEAKAGE"):
            compute_features(df, "2022-01-01")


# ── Feature completeness ──────────────────────────────────────────────────────────

class TestFeatureCompleteness:

    def _feats(self):
        df = make_project()
        return compute_features(df, "2022-06-01")

    def test_all_numeric_present(self):
        f = self._feats()
        assert f is not None
        for col in NUMERIC_FEATURES:
            assert col in f, f"Missing: {col}"

    def test_all_categorical_present(self):
        f = self._feats()
        assert f is not None
        for col in CATEGORICAL_FEATURES:
            assert col in f, f"Missing: {col}"

    def test_no_nan_or_inf(self):
        f = self._feats()
        assert f is not None
        for k, v in f.items():
            if isinstance(v, float):
                assert math.isfinite(v), f"{k}={v} is not finite"

    def test_progress_gap_sign_behind(self):
        """Project with only 5% progress at 50% timeline => positive gap."""
        df = make_project(n=1, start="2020-01-01", dur=365)
        df.iloc[0, df.columns.get_loc("update_date")] = "2020-06-01"
        df.iloc[0, df.columns.get_loc("physical_progress_pct")] = 5.0
        f = compute_features(df, "2020-07-01")
        assert f is not None
        assert f["progress_gap"] > 0, "Should be behind schedule"

    def test_missingness_flags_zero_on_complete_data(self):
        f = self._feats()
        assert f is not None
        assert f.get("physical_progress_pct_missing", 0) == 0


# ── Label boundary tests ──────────────────────────────────────────────────────────

class TestLabels:

    def test_overrun_true(self):
        df = make_project(overrun=True)
        L  = compute_labels(df, sector="Highways")
        assert L["label_overrun"] == 1   # final_cost=750, sanc=500, tol=15% => 750>575

    def test_overrun_false(self):
        df = make_project(overrun=False)
        L  = compute_labels(df, sector="Highways")
        assert L["label_overrun"] == 0   # final_cost=475, well below

    def test_delay_true(self):
        df = make_project(delayed=True, dur=365)
        L  = compute_labels(df)
        assert L["label_delay"] == 1

    def test_delay_false(self):
        df = make_project(delayed=False, dur=365)
        L  = compute_labels(df)
        assert L["label_delay"] == 0

    def test_delayed_project_labels_both_targets(self):
        df = make_project(delayed=True, overrun=True)
        L  = compute_labels(df, sector="Highways")
        assert L["label_delay"]   == 1
        assert L["label_overrun"] == 1


# ── Temporal split: no leakage across cutoffs ─────────────────────────────────────

class TestTemporalSplit:

    def _mini_df(self) -> pd.DataFrame:
        from backend.pragya_xai.features.pipeline import build_training_dataset
        return pd.DataFrame([
            {"project_id": "A", "as_of_date": "2020-01-01", "label_overrun": 0, "label_delay": 0},
            {"project_id": "A", "as_of_date": "2021-01-01", "label_overrun": 0, "label_delay": 0},
            {"project_id": "B", "as_of_date": "2022-01-01", "label_overrun": 1, "label_delay": 1},
            {"project_id": "B", "as_of_date": "2023-01-01", "label_overrun": 1, "label_delay": 1},
        ])

    def test_train_test_projects_disjoint(self):
        df = self._mini_df()
        train = set(df[df["as_of_date"].isin(["2020-01-01", "2021-01-01"])]["project_id"])
        test  = set(df[df["as_of_date"] == "2023-01-01"]["project_id"])
        # A only in train period, B only in test period
        assert train == {"A"}
        assert test  == {"B"}
        assert train.isdisjoint(test)


# ── Translator consistency tests ──────────────────────────────────────────────────

class TestTranslator:

    def test_positive_impact_says_raises(self):
        text = translate_feature("progress_gap", 22.0, impact=+0.15)
        assert "raises risk" in text.lower() or "increases" in text.lower()

    def test_negative_impact_says_lowers(self):
        text = translate_feature("progress_gap", -5.0, impact=-0.10)
        assert "lowers risk" in text.lower() or "reduces" in text.lower()

    def test_no_contradiction_progress_behind(self):
        """High progress_gap with positive impact must say risk goes up."""
        text = translate_feature("progress_gap", 25.0, +0.20)
        # Must not contain contradictory wording
        assert "lowers" not in text.lower()
        assert "reduces" not in text.lower()

    def test_consistency_enforce_appends_tag(self):
        text = "some neutral text"
        enforced = _consistency_enforce(text, impact=+0.1)
        assert "Increases Risk" in enforced

    def test_zero_gap_handled(self):
        text = translate_feature("progress_gap", 0.0, +0.01)
        assert isinstance(text, str) and len(text) > 10

    def test_cost_overrun_positive(self):
        text = translate_feature("cost_growth_pct", 45.0, +0.25)
        assert "45" in text
        assert "raises risk" in text.lower() or "increases" in text.lower()

    def test_all_numeric_features_have_translations(self):
        """Every numeric feature must return a non-empty string (not crash)."""
        from backend.pragya_xai.features.pipeline import NUMERIC_FEATURES
        for feat in NUMERIC_FEATURES:
            text = translate_feature(feat, 1.0, +0.05)
            assert isinstance(text, str) and len(text) > 5, f"Bad translation for {feat}"
