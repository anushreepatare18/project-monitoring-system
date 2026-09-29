import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Create synthetic dataset for 1981 projects based on the PDF structure
np.random.seed(42)
random.seed(42)

ministries = ['Road Transport', 'Railways', 'Petroleum & Natural Gas', 'Power', 'Coal', 'Urban Affairs', 'Water Resources']
states = ['Maharashtra', 'Uttar Pradesh', 'Gujarat', 'Madhya Pradesh', 'Karnataka', 'Odisha', 'Bihar']

n_projects = 1981

data = []
for i in range(1, n_projects + 1):
    original_cost = round(random.uniform(150, 10000), 2)
    # 30% chance of cost overrun
    has_overrun = random.random() < 0.3
    if has_overrun:
        revised_cost = round(original_cost * random.uniform(1.05, 1.8), 2)
    else:
        revised_cost = original_cost
        
    expenditure = round(revised_cost * random.uniform(0.1, 0.95), 2)
    physical_progress = round((expenditure / revised_cost) * 100 + random.uniform(-10, 15), 2)
    physical_progress = min(max(physical_progress, 0), 100)
    
    # Dates
    start_date = datetime(2018, 1, 1) + timedelta(days=random.randint(0, 2000))
    original_target_date = start_date + timedelta(days=random.randint(500, 1500))
    
    # 40% chance of delay
    has_delay = random.random() < 0.4
    if has_delay:
        revised_target_date = original_target_date + timedelta(days=random.randint(30, 730))
    else:
        revised_target_date = original_target_date
        
    delay_months = max(0, (revised_target_date - original_target_date).days // 30)
    
    # Outcome variable for ML: High Risk if delay > 6 months or cost overrun > 15%
    cost_overrun_pct = ((revised_cost - original_cost) / original_cost) * 100
    is_high_risk = int((delay_months > 6) or (cost_overrun_pct > 15))
    
    data.append({
        'Project_ID': f'PRJ-{i:04d}',
        'Ministry': random.choice(ministries),
        'State': random.choice(states),
        'Original_Cost_Cr': original_cost,
        'Revised_Cost_Cr': revised_cost,
        'Expenditure_Cr': expenditure,
        'Physical_Progress_Pct': physical_progress,
        'Start_Date': start_date.strftime('%Y-%m-%d'),
        'Original_Target_Date': original_target_date.strftime('%Y-%m-%d'),
        'Revised_Target_Date': revised_target_date.strftime('%Y-%m-%d'),
        'Delay_Months': delay_months,
        'Cost_Overrun_Pct': round(cost_overrun_pct, 2),
        'Is_High_Risk': is_high_risk
    })

df = pd.DataFrame(data)
df.to_csv('project_data.csv', index=False)
print(f"Generated {n_projects} synthetic projects in project_data.csv")
