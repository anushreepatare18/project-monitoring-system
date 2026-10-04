import pytest
import pandas as pd
from ml_core.features.pipeline import compute_features

def test_leakage_raises_error():
    data = pd.DataFrame({
        "project_id": ["P1", "P1"],
        "update_date": ["2026-01-01", "2026-05-01"],
        "physical_progress_pct": [10, 50],
        "planned_start": ["2025-01-01", "2025-01-01"],
        "planned_end": ["2026-12-31", "2026-12-31"],
        "expected_completion_date": ["2026-12-31", "2026-12-31"],
        "milestone_planned_date": ["2025-06-01", "2025-06-01"],
        "milestone_actual_date": ["2025-06-05", "2025-06-05"],
        "revised_cost": [100, 100],
        "sanctioned_cost": [100, 100],
        "cumulative_expenditure": [10, 50],
        "sector": ["A", "A"],
        "ministry": ["B", "B"],
        "agency": ["C", "C"],
        "state": ["D", "D"],
        "project_type": ["E", "E"]
    })
    
    # Passing an as_of_date BEFORE the latest update should raise an AssertionError
    with pytest.raises(AssertionError, match="LEAKAGE DETECTED"):
        compute_features(data, "2026-03-01")

def test_no_leakage_passes():
    data = pd.DataFrame({
        "project_id": ["P1", "P1"],
        "update_date": ["2026-01-01", "2026-05-01"],
        "physical_progress_pct": [10, 50],
        "planned_start": ["2025-01-01", "2025-01-01"],
        "planned_end": ["2026-12-31", "2026-12-31"],
        "expected_completion_date": ["2026-12-31", "2026-12-31"],
        "milestone_planned_date": ["2025-06-01", "2025-06-01"],
        "milestone_actual_date": ["2025-06-05", "2025-06-05"],
        "revised_cost": [100, 100],
        "sanctioned_cost": [100, 100],
        "cumulative_expenditure": [10, 50],
        "sector": ["A", "A"],
        "ministry": ["B", "B"],
        "agency": ["C", "C"],
        "state": ["D", "D"],
        "project_type": ["E", "E"]
    })
    
    # Calling with a date equal to or after all updates should succeed
    features = compute_features(data, "2026-06-01")
    assert len(features) == 1
    assert "progress_gap" in features.columns
