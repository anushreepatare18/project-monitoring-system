import pytest
import pandas as pd
from datetime import datetime, timedelta
from ..features.pipeline import compute_features

def test_leakage_check_raises_error():
    df = pd.DataFrame([
        {
            'update_date': '2023-01-01',
            'physical_progress_pct': 10,
            'cumulative_expenditure': 100,
            'planned_start': '2022-01-01',
            'planned_end': '2024-01-01',
            'sector': 'A', 'ministry': 'B', 'agency': 'C'
        },
        {
            'update_date': '2023-06-01',
            'physical_progress_pct': 20,
            'cumulative_expenditure': 200,
            'planned_start': '2022-01-01',
            'planned_end': '2024-01-01',
            'sector': 'A', 'ministry': 'B', 'agency': 'C'
        }
    ])
    
    # Passing an as_of_date that is BEFORE some updates in the dataframe
    with pytest.raises(ValueError, match="LEAKAGE DETECTED"):
        compute_features(df, '2023-03-01')

def test_no_leakage_works():
    df = pd.DataFrame([
        {
            'update_date': '2023-01-01',
            'physical_progress_pct': 10,
            'cumulative_expenditure': 100,
            'planned_start': '2022-01-01',
            'planned_end': '2024-01-01',
            'sector': 'A', 'ministry': 'B', 'agency': 'C'
        }
    ])
    
    # as_of_date is exactly or after the updates
    features = compute_features(df, '2023-02-01')
    assert features is not None
    assert 'progress_gap' in features
