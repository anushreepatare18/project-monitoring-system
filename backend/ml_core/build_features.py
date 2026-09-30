import pandas as pd
import numpy as np
import os
from features.pipeline import build_dataset_for_horizon

def main():
    print("Loading dataset.csv...")
    if not os.path.exists("dataset.csv"):
        print("dataset.csv not found! Run python backend/ml_core/data/generator.py first.")
        return
        
    df = pd.read_csv("dataset.csv")
    
    # We will choose 3 cutoff dates: 
    # Since projects started between 2018 and 2023, and take 1-5 years.
    # T1: 2020-01-01 (Train)
    # T2: 2021-01-01 (Train)
    # T3: 2022-01-01 (Train/Val)
    # T4: 2023-01-01 (Val/Test)
    # T5: 2024-01-01 (Test)
    
    cutoffs = ['2020-01-01', '2021-01-01', '2022-01-01', '2023-01-01', '2024-01-01']
    
    print("Building point-in-time features. This may take a moment...")
    
    # We must ensure that we pass TRUNCATED data to the pipeline to satisfy the leakage check.
    # For build_dataset_for_horizon, we pass the full df, and it loops over projects, but wait,
    # the pipeline's compute_features raises an error if ANY date is > as_of_date.
    # So we MUST truncate the df before passing it to compute_features.
    
    # Let's fix this here by truncating per cutoff.
    all_records = []
    
    for as_of in cutoffs:
        print(f"Processing cutoff date: {as_of}")
        # Truncate dataset up to the cutoff date for features
        df_up_to_cutoff = df[pd.to_datetime(df['update_date']) <= pd.to_datetime(as_of)].copy()
        
        # We need the full dataframe for labels (final_cost, final_end_date etc)
        # build_dataset_for_horizon takes the full df, but it needs to pass only truncated
        # Let's just use build_dataset_for_horizon but we need to modify it or do it here.
        
        # Actually, let's call the logic directly here to be safe with leakage check.
        from features.pipeline import compute_features
        
        for pid, grp_full in df.groupby('project_id'):
            # Only consider if project was active before as_of
            grp_past = grp_full[pd.to_datetime(grp_full['update_date']) <= pd.to_datetime(as_of)].copy()
            
            if grp_past.empty:
                continue
                
            try:
                feats = compute_features(grp_past, as_of)
                if not feats:
                    continue
                    
                full_latest = grp_full.iloc[-1]
                sanc_cost = full_latest['sanctioned_cost']
                if sanc_cost == 0: sanc_cost = 1
                
                planned_start = pd.to_datetime(full_latest['planned_start'])
                planned_end = pd.to_datetime(full_latest['planned_end'])
                final_end = pd.to_datetime(full_latest['final_end_date'])
                final_cost = full_latest['final_cost']
                
                tol_time = max(90, (planned_end - planned_start).days * 0.1)
                
                label_overrun = 1 if final_cost > sanc_cost * 1.1 else 0
                label_delay = 1 if (final_end - planned_end).days > tol_time else 0
                
                # Impl risk
                future = grp_full[(pd.to_datetime(grp_full['update_date']) > pd.to_datetime(as_of)) & 
                                  (pd.to_datetime(grp_full['update_date']) <= pd.to_datetime(as_of) + pd.Timedelta(days=180))]
                label_impl_risk = 0
                if not future.empty:
                    prog_gain = future['physical_progress_pct'].max() - feats.get('physical_progress_pct', grp_past['physical_progress_pct'].iloc[-1])
                    if prog_gain < 2.0:
                        label_impl_risk = 1
                elif label_delay == 1:
                    label_impl_risk = 1
                
                rec = {'project_id': pid, 'as_of_date': as_of}
                rec.update(feats)
                rec['label_overrun'] = label_overrun
                rec['label_delay'] = label_delay
                rec['label_impl_risk'] = label_impl_risk
                
                all_records.append(rec)
                
            except ValueError as e:
                print(f"Leakage check failed for {pid}: {e}")
                
    features_df = pd.DataFrame(all_records)
    
    # Split temporally
    print(f"Total features extracted: {len(features_df)} rows")
    
    # Train: 2020, 2021, 2022
    # Val: 2023
    # Test: 2024
    train_df = features_df[features_df['as_of_date'].isin(['2020-01-01', '2021-01-01', '2022-01-01'])]
    val_df = features_df[features_df['as_of_date'] == '2023-01-01']
    test_df = features_df[features_df['as_of_date'] == '2024-01-01']
    
    os.makedirs('backend/ml_core/data/processed', exist_ok=True)
    train_df.to_csv('backend/ml_core/data/processed/train.csv', index=False)
    val_df.to_csv('backend/ml_core/data/processed/val.csv', index=False)
    test_df.to_csv('backend/ml_core/data/processed/test.csv', index=False)
    
    print("Saved train.csv, val.csv, test.csv in backend/ml_core/data/processed/")

if __name__ == "__main__":
    main()
