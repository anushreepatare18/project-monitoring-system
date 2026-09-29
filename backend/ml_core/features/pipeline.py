import pandas as pd
import numpy as np
from datetime import datetime

def compute_features(project_df: pd.DataFrame, as_of_date: str) -> dict:
    """
    Computes features for a single project as of a specific date.
    project_df: DataFrame containing all updates for ONE project.
    as_of_date: string 'YYYY-MM-DD'
    
    Returns a dictionary of features.
    """
    as_of = pd.to_datetime(as_of_date)
    
    # Leakage check: ensure no future data is in the dataframe we process
    project_df['update_date'] = pd.to_datetime(project_df['update_date'])
    if (project_df['update_date'] > as_of).any():
        raise ValueError(f"LEAKAGE DETECTED: Data contains updates after as_of_date {as_of_date}")
    
    # Sort chronologically
    df_past = project_df[project_df['update_date'] <= as_of].sort_values('update_date').copy()
    
    if df_past.empty:
        return None # No data available as of this date
        
    latest = df_past.iloc[-1]
    
    # Impute missing with flags
    features = {}
    missing_flags = {}
    
    def get_val(col, default=0.0):
        val = latest.get(col, pd.NA)
        if pd.isna(val):
            missing_flags[f"{col}_missing"] = 1
            return default
        missing_flags[f"{col}_missing"] = 0
        return float(val)
        
    actual_progress = get_val('physical_progress_pct')
    sanctioned_cost = get_val('sanctioned_cost', 1.0)
    if sanctioned_cost == 0: sanctioned_cost = 1.0 # avoid div by zero
    expenditure = get_val('cumulative_expenditure')
    revised_cost = get_val('revised_cost', sanctioned_cost)
    
    # Dates
    planned_start = pd.to_datetime(latest['planned_start'])
    planned_end = pd.to_datetime(latest['planned_end'])
    
    # Progress gap
    total_planned_days = (planned_end - planned_start).days
    days_elapsed = (as_of - planned_start).days
    
    expected_progress = 0.0
    if total_planned_days > 0:
        expected_progress = min(100.0, max(0.0, (days_elapsed / total_planned_days) * 100))
        
    features['progress_gap'] = expected_progress - actual_progress
    
    # Velocity
    df_past['days_diff'] = df_past['update_date'].diff().dt.days
    df_past['prog_diff'] = df_past['physical_progress_pct'].diff()
    df_past['velocity_per_day'] = df_past['prog_diff'] / df_past['days_diff'].replace(0, np.nan)
    
    def get_velocity(n):
        if len(df_past) > 1:
            recent = df_past.tail(n+1)
            prog_gained = recent['physical_progress_pct'].iloc[-1] - recent['physical_progress_pct'].iloc[0]
            days_passed = (recent['update_date'].iloc[-1] - recent['update_date'].iloc[0]).days
            if days_passed > 0:
                return prog_gained / days_passed
        return 0.0
        
    features['velocity_last_1'] = get_velocity(1)
    features['velocity_last_3'] = get_velocity(3)
    features['velocity_last_6'] = get_velocity(6)
    
    progress_remaining = 100.0 - actual_progress
    days_remaining_to_plan = (planned_end - as_of).days
    
    if days_remaining_to_plan > 0:
        features['velocity_needed_to_finish'] = progress_remaining / days_remaining_to_plan
    else:
        features['velocity_needed_to_finish'] = 999.0 if progress_remaining > 0 else 0.0
        
    # Milestones
    # We aggregate all milestones up to this point
    milestones = df_past[['milestone_name', 'milestone_planned_date', 'milestone_expected_date', 'milestone_actual_date']].dropna(subset=['milestone_name'])
    max_m_delay = 0
    delayed_count = 0
    total_m = len(milestones['milestone_name'].unique())
    
    if total_m > 0:
        for _, m in milestones.groupby('milestone_name').last().iterrows():
            m_planned = pd.to_datetime(m['milestone_planned_date'])
            if pd.notna(m['milestone_actual_date']):
                m_actual = pd.to_datetime(m['milestone_actual_date'])
                delay = (m_actual - m_planned).days / 30.0
            elif pd.notna(m['milestone_expected_date']):
                m_exp = pd.to_datetime(m['milestone_expected_date'])
                delay = (m_exp - m_planned).days / 30.0
            else:
                delay = 0
                
            if delay > 0:
                delayed_count += 1
                max_m_delay = max(max_m_delay, delay)
                
        features['pct_milestones_delayed'] = delayed_count / total_m
    else:
        features['pct_milestones_delayed'] = 0.0
        missing_flags['milestone_data_missing'] = 1
        
    features['max_milestone_delay_months'] = max_m_delay
    
    # Cost
    features['cost_growth_pct'] = ((revised_cost - sanctioned_cost) / sanctioned_cost) * 100
    features['expenditure_to_progress_ratio'] = (expenditure / sanctioned_cost) / (actual_progress / 100.0) if actual_progress > 0 else 0
    
    # Burn rate (cost per day over last 3 updates)
    if len(df_past) > 3:
        recent = df_past.tail(4)
        cost_spent = recent['cumulative_expenditure'].iloc[-1] - recent['cumulative_expenditure'].iloc[0]
        days_passed = (recent['update_date'].iloc[-1] - recent['update_date'].iloc[0]).days
        features['burn_rate_per_day'] = cost_spent / days_passed if days_passed > 0 else 0
    else:
        features['burn_rate_per_day'] = 0.0
        
    # Updates
    features['days_since_last_update'] = (as_of - df_past['update_date'].iloc[-1]).days
    features['avg_update_gap'] = df_past['days_diff'].mean() if len(df_past) > 1 else 0.0
    features['count_of_revised_dates'] = df_past['expected_completion_date'].nunique() - 1 if df_past['expected_completion_date'].nunique() > 1 else 0
    
    # Categoricals
    features['sector'] = latest['sector']
    features['ministry'] = latest['ministry']
    features['agency'] = latest['agency']
    
    # Merge missing flags
    features.update(missing_flags)
    
    # Ensure no NaN
    for k, v in features.items():
        if pd.isna(v):
            features[k] = 0.0
            
    return features

def build_dataset_for_horizon(df: pd.DataFrame, as_of_dates: list) -> pd.DataFrame:
    """
    Builds a dataset across multiple as_of_dates for training/eval.
    """
    records = []
    
    # Label logic: final_cost > sanctioned * 1.1, time_delay > planned + max(90 days, 10% duration)
    # Implementation risk: max_milestone_delay > 3 months OR velocity < needed / 2
    
    for as_of in as_of_dates:
        # For each project, if it started before as_of and outcome is known AFTER as_of (to prevent target leakage)
        # Actually, we can train on any project, the outcome is in final_* columns
        
        for pid, grp in df.groupby('project_id'):
            # Only consider if project was active or outcome known
            first_update = pd.to_datetime(grp['update_date'].min())
            if first_update > pd.to_datetime(as_of):
                continue
                
            try:
                feats = compute_features(grp, as_of)
                if not feats:
                    continue
                    
                latest = grp[pd.to_datetime(grp['update_date']) <= pd.to_datetime(as_of)].iloc[-1]
                
                # Labels (computed from full data, NOT the truncated past data)
                # But we must only use 'final_' columns which are constant for a project.
                full_latest = grp.iloc[-1]
                
                sanc_cost = full_latest['sanctioned_cost']
                if sanc_cost == 0: sanc_cost = 1
                
                planned_start = pd.to_datetime(full_latest['planned_start'])
                planned_end = pd.to_datetime(full_latest['planned_end'])
                final_end = pd.to_datetime(full_latest['final_end_date'])
                final_cost = full_latest['final_cost']
                
                # Tolerance
                tol_time = max(90, (planned_end - planned_start).days * 0.1)
                
                label_overrun = 1 if final_cost > sanc_cost * 1.1 else 0
                label_delay = 1 if (final_end - planned_end).days > tol_time else 0
                
                # Impl risk: check forward window 6 months from as_of
                future = grp[(pd.to_datetime(grp['update_date']) > pd.to_datetime(as_of)) & 
                             (pd.to_datetime(grp['update_date']) <= pd.to_datetime(as_of) + pd.Timedelta(days=180))]
                
                label_impl_risk = 0
                if not future.empty:
                    prog_gain = future['physical_progress_pct'].max() - feats.get('physical_progress_pct', latest['physical_progress_pct'])
                    if prog_gain < 2.0: # Stagnation
                        label_impl_risk = 1
                elif label_delay == 1:
                    label_impl_risk = 1 # Fallback
                
                rec = {'project_id': pid, 'as_of_date': as_of}
                rec.update(feats)
                rec['label_overrun'] = label_overrun
                rec['label_delay'] = label_delay
                rec['label_impl_risk'] = label_impl_risk
                
                records.append(rec)
            except ValueError as e:
                # Leakage detected
                raise e
                
    return pd.DataFrame(records)
