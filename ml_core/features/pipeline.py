import pandas as pd
import numpy as np
from datetime import datetime

def compute_features(df_history: pd.DataFrame, as_of_date: str) -> pd.DataFrame:
    """
    Compute features for projects valid on or before as_of_date.
    Throws AssertionError if any row has an update_date > as_of_date (Leakage check).
    """
    df = df_history.copy()
    
    # Ensure datetime parsing
    date_cols = ['update_date', 'planned_start', 'planned_end', 'expected_completion_date', 'milestone_planned_date', 'milestone_actual_date']
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce')
        
    as_of = pd.to_datetime(as_of_date)
    
    # LEAKAGE CHECK
    if (df['update_date'] > as_of).any():
        raise AssertionError(f"LEAKAGE DETECTED: Data contains updates after as_of_date {as_of_date}")
        
    # We only care about the latest record per project as of the date for cross-sectional inference
    df = df.sort_values(by=['project_id', 'update_date'])
    
    # Calculate velocities using history before groupby tail(1)
    df['prev_physical_progress'] = df.groupby('project_id')['physical_progress_pct'].shift(1)
    df['prev_update_date'] = df.groupby('project_id')['update_date'].shift(1)
    
    df['days_since_last_update'] = (df['update_date'] - df['prev_update_date']).dt.days
    df['progress_velocity'] = df['physical_progress_pct'] - df['prev_physical_progress']
    
    # Now get the latest row per project as of the date
    latest = df.groupby('project_id').tail(1).copy()
    
    # Time based expected progress (linear interpolation)
    latest['total_planned_days'] = (latest['planned_end'] - latest['planned_start']).dt.days
    latest['days_elapsed'] = (latest['update_date'] - latest['planned_start']).dt.days
    latest['expected_progress'] = (latest['days_elapsed'] / latest['total_planned_days'].replace(0, 1)) * 100
    latest['expected_progress'] = latest['expected_progress'].clip(0, 100)
    
    # Features
    latest['progress_gap'] = latest['expected_progress'] - latest['physical_progress_pct']
    
    # Velocity needed to finish on time
    latest['days_remaining_planned'] = (latest['planned_end'] - latest['update_date']).dt.days
    latest['progress_remaining'] = 100.0 - latest['physical_progress_pct']
    latest['velocity_needed'] = np.where(latest['days_remaining_planned'] > 0, 
                                         latest['progress_remaining'] / latest['days_remaining_planned'], 
                                         999) # arbitrary high number if past deadline and incomplete
                                         
    # Milestone delay
    latest['milestone_delay_days'] = (latest['update_date'] - latest['milestone_planned_date']).dt.days
    latest['milestone_delay_days'] = np.where(latest['milestone_actual_date'].isna() & (latest['milestone_delay_days'] > 0), 
                                              latest['milestone_delay_days'], 0)
    latest['max_milestone_delay_months'] = latest['milestone_delay_days'] / 30.0
    latest['pct_milestones_delayed'] = np.where(latest['max_milestone_delay_months'] > 0, 1.0, 0.0) # simplify for 1 milestone
    
    # Cost features
    latest['cost_growth_pct'] = ((latest['revised_cost'] - latest['sanctioned_cost']) / latest['sanctioned_cost'].replace(0, 1)) * 100
    latest['expenditure_to_progress_ratio'] = latest['cumulative_expenditure'] / (latest['physical_progress_pct'].replace(0, 1) / 100 * latest['sanctioned_cost'].replace(0, 1))
    
    # Impute missing velocity with median or 0
    latest['progress_velocity'] = latest['progress_velocity'].fillna(0)
    latest['days_since_last_update'] = latest['days_since_last_update'].fillna(0)
    latest['avg_update_gap'] = latest['days_since_last_update'] # Simplified
    latest['count_of_revised_dates'] = np.where(latest['expected_completion_date'] > latest['planned_end'], 1, 0)
    
    # Missingness indicators
    latest['missing_velocity_flag'] = latest['prev_physical_progress'].isna().astype(int)
    
    features = [
        'project_id', 'sector', 'ministry', 'agency', 'state', 'project_type',
        'progress_gap', 'progress_velocity', 'velocity_needed',
        'max_milestone_delay_months', 'pct_milestones_delayed',
        'cost_growth_pct', 'expenditure_to_progress_ratio',
        'days_since_last_update', 'avg_update_gap', 'count_of_revised_dates',
        'missing_velocity_flag'
    ]
    
    return latest[features].set_index('project_id')
