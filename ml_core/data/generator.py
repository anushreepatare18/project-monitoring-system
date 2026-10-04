import pandas as pd
import numpy as np
import datetime
import random
import os

def generate_synthetic_data(num_projects=2000, output_file="synthetic_projects.csv"):
    np.random.seed(42)
    random.seed(42)
    
    sectors = [f"Sector_{i}" for i in range(1, 21)]
    ministries = [f"Ministry_{i}" for i in range(1, 10)]
    agencies = [f"Agency_{i}" for i in range(1, 50)]
    states = ["MH", "KA", "DL", "UP", "TN", "GJ", "WB", "RJ", "MP", "AP"]
    project_types = ["Infrastructure", "IT", "Research", "Construction", "Policy"]
    
    records = []
    
    for i in range(num_projects):
        project_id = f"PRJ-{np.random.randint(1000, 999999):06d}"
        sector = random.choice(sectors)
        ministry = random.choice(ministries)
        agency = random.choice(agencies)
        state = random.choice(states)
        p_type = random.choice(project_types)
        
        sanctioned_cost = round(np.random.uniform(10, 5000), 2)
        
        start_date = datetime.date(2018, 1, 1) + datetime.timedelta(days=random.randint(0, 1500))
        duration_days = random.randint(300, 1500)
        planned_end = start_date + datetime.timedelta(days=duration_days)
        
        # Decide if delayed or overrun for labels
        is_delayed = np.random.rand() < 0.3
        is_overrun = np.random.rand() < 0.25
        
        actual_duration = duration_days * (random.uniform(1.1, 1.5) if is_delayed else random.uniform(0.9, 1.05))
        final_end_date = start_date + datetime.timedelta(days=int(actual_duration))
        final_cost = sanctioned_cost * (random.uniform(1.1, 1.4) if is_overrun else random.uniform(0.95, 1.05))
        
        outcome_known_at = final_end_date + datetime.timedelta(days=30)
        
        num_updates = random.randint(5, 12)
        update_interval = actual_duration / num_updates
        
        # Determine anomaly update index
        anomaly_idx = random.randint(1, num_updates-2) if np.random.rand() < 0.1 else -1
        
        for u in range(num_updates):
            update_date = start_date + datetime.timedelta(days=int((u+1)*update_interval))
            if update_date > final_end_date:
                update_date = final_end_date
            
            progress_ratio = (update_date - start_date).days / actual_duration
            physical_progress = min(100.0, progress_ratio * 100 * random.uniform(0.8, 1.2))
            financial_progress = min(100.0, progress_ratio * 100 * random.uniform(0.8, 1.2))
            
            cumulative_expenditure = (financial_progress / 100) * final_cost
            
            # Inject anomaly
            if u == anomaly_idx:
                cumulative_expenditure *= 2.5 # Sudden spike
                physical_progress = max(0, physical_progress - 20) # Implausible drop
                
            revised_cost = sanctioned_cost
            if is_overrun and u > num_updates // 2:
                revised_cost = final_cost * random.uniform(0.9, 1.0)
                
            expected_completion_date = planned_end
            if is_delayed and u > num_updates // 3:
                expected_completion_date = final_end_date - datetime.timedelta(days=random.randint(0, 60))
                
            milestone_planned = start_date + datetime.timedelta(days=duration_days//2)
            
            records.append({
                "project_id": project_id,
                "update_date": update_date.strftime("%Y-%m-%d"),
                "ministry": ministry,
                "sector": sector,
                "agency": agency,
                "state": state,
                "sanctioned_cost": sanctioned_cost,
                "planned_start": start_date.strftime("%Y-%m-%d"),
                "planned_end": planned_end.strftime("%Y-%m-%d"),
                "project_type": p_type,
                "physical_progress_pct": round(physical_progress, 2),
                "financial_progress_pct": round(financial_progress, 2),
                "cumulative_expenditure": round(cumulative_expenditure, 2),
                "revised_cost": round(revised_cost, 2),
                "expected_completion_date": expected_completion_date.strftime("%Y-%m-%d"),
                "milestone_name": "Mid-Point Review",
                "milestone_planned_date": milestone_planned.strftime("%Y-%m-%d"),
                "milestone_expected_date": (milestone_planned + datetime.timedelta(days=30)).strftime("%Y-%m-%d") if is_delayed else milestone_planned.strftime("%Y-%m-%d"),
                "milestone_actual_date": (milestone_planned + datetime.timedelta(days=int(actual_duration/2))).strftime("%Y-%m-%d") if update_date > milestone_planned else "",
                "final_cost": round(final_cost, 2),
                "final_end_date": final_end_date.strftime("%Y-%m-%d"),
                "delayed_flag": 1 if is_delayed else 0,
                "overrun_flag": 1 if is_overrun else 0,
                "outcome_known_at": outcome_known_at.strftime("%Y-%m-%d")
            })
            
    df = pd.DataFrame(records)
    
    # Sort by time
    df['update_date'] = pd.to_datetime(df['update_date'])
    df = df.sort_values(by='update_date')
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df.to_csv(output_file, index=False)
    print(f"Generated {len(df)} updates across {num_projects} projects in {output_file}")
    return df

if __name__ == "__main__":
    generate_synthetic_data(output_file="ml_core/data/synthetic_projects.csv")
