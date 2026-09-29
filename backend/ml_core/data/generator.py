import pandas as pd
import numpy as np
from datetime import timedelta, datetime
import uuid

def generate_synthetic_data(num_projects=2000, random_seed=42):
    np.random.seed(random_seed)
    
    ministries = [f"Ministry_{i}" for i in range(1, 11)]
    sectors = [f"Sector_{i}" for i in range(1, 21)]
    states = ["Delhi", "Maharashtra", "Karnataka", "Tamil Nadu", "Gujarat", "UP", "MP"]
    project_types = ["Infrastructure", "IT", "Research", "Defense", "Healthcare"]
    
    records = []
    
    for _ in range(num_projects):
        project_id = f"PRJ-{uuid.uuid4().hex[:8].upper()}"
        ministry = np.random.choice(ministries)
        sector = np.random.choice(sectors)
        agency = f"Agency_{np.random.randint(1, 50)}"
        state = np.random.choice(states)
        project_type = np.random.choice(project_types)
        
        sanctioned_cost = np.round(np.random.lognormal(mean=4, sigma=1) * 10, 2)
        
        # Start date between 2018 and 2023
        start_date = datetime(2018, 1, 1) + timedelta(days=np.random.randint(0, 1800))
        planned_duration_days = np.random.randint(365, 365*5)
        planned_end = start_date + timedelta(days=planned_duration_days)
        
        # Outcomes
        is_delayed = np.random.rand() < 0.3
        is_overrun = np.random.rand() < 0.25
        
        final_end_date = planned_end + timedelta(days=np.random.randint(90, 730)) if is_delayed else planned_end - timedelta(days=np.random.randint(0, 60))
        final_cost = sanctioned_cost * np.random.uniform(1.15, 2.5) if is_overrun else sanctioned_cost * np.random.uniform(0.9, 1.05)
        
        outcome_known_at = final_end_date
        
        num_updates = np.random.randint(5, 13)
        update_dates = [start_date + timedelta(days=(final_end_date - start_date).days * (i / num_updates)) for i in range(1, num_updates + 1)]
        
        # Generate updates
        current_expenditure = 0
        current_physical = 0
        current_financial = 0
        
        for i, update_date in enumerate(update_dates):
            # Add anomalies randomly
            is_anomalous_update = np.random.rand() < 0.02
            
            # Progress logic
            progress_fraction = (i + 1) / num_updates
            
            if is_anomalous_update:
                current_physical += np.random.uniform(20, 40) # Implausible jump
                current_expenditure += sanctioned_cost * np.random.uniform(0.3, 0.5)
            else:
                # Normal progression
                current_physical = min(100.0, np.random.normal(loc=progress_fraction * 100, scale=5))
                current_expenditure = min(final_cost, np.random.normal(loc=progress_fraction * final_cost, scale=final_cost*0.05))
                
            current_physical = max(0, min(100.0, current_physical))
            current_financial = (current_expenditure / sanctioned_cost) * 100
            
            revised_cost = sanctioned_cost
            if is_overrun and i > num_updates / 2:
                revised_cost = final_cost * np.random.uniform(0.95, 1.05)
                
            expected_completion = planned_end
            if is_delayed and i > num_updates / 3:
                expected_completion = final_end_date
            
            # Milestones
            milestone_name = f"Milestone_{i}"
            m_planned = start_date + timedelta(days=planned_duration_days * progress_fraction)
            m_expected = expected_completion - timedelta(days=(num_updates - i)*30)
            m_actual = update_date if current_physical > progress_fraction * 100 else None
            
            records.append({
                "project_id": project_id,
                "update_date": update_date.strftime("%Y-%m-%d"),
                "ministry": ministry,
                "sector": sector,
                "agency": agency,
                "state": state,
                "sanctioned_cost": round(sanctioned_cost, 2),
                "planned_start": start_date.strftime("%Y-%m-%d"),
                "planned_end": planned_end.strftime("%Y-%m-%d"),
                "project_type": project_type,
                "physical_progress_pct": round(current_physical, 2),
                "financial_progress_pct": round(current_financial, 2),
                "cumulative_expenditure": round(current_expenditure, 2),
                "revised_cost": round(revised_cost, 2),
                "expected_completion_date": expected_completion.strftime("%Y-%m-%d"),
                "milestone_name": milestone_name,
                "milestone_planned_date": m_planned.strftime("%Y-%m-%d"),
                "milestone_expected_date": m_expected.strftime("%Y-%m-%d"),
                "milestone_actual_date": m_actual.strftime("%Y-%m-%d") if m_actual else None,
                "final_cost": round(final_cost, 2),
                "final_end_date": final_end_date.strftime("%Y-%m-%d"),
                "delayed_flag": int(is_delayed),
                "overrun_flag": int(is_overrun),
                "outcome_known_at": outcome_known_at.strftime("%Y-%m-%d")
            })
            
    df = pd.DataFrame(records)
    return df

if __name__ == "__main__":
    df = generate_synthetic_data()
    output_path = "dataset.csv"
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} project update records across {df['project_id'].nunique()} projects.")
    print(f"Saved to {output_path}")
