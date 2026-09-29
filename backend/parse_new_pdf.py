import re
import pandas as pd
from datetime import datetime
import random

def parse_date(date_str):
    if not date_str or date_str == '-' or date_str == 'NA':
        return None
    try:
        return datetime.strptime(date_str, '%m/%Y')
    except:
        return None

def main():
    raw_path = r"c:\Users\RAMESH PATARE\OneDrive\Desktop\SIH\SIH26103\backend\raw_data_2.txt"
    csv_path = r"c:\Users\RAMESH PATARE\OneDrive\Desktop\SIH\SIH26103\backend\project_data.csv"
    
    try:
        existing_df = pd.read_csv(csv_path)
        last_id_str = existing_df['Project_ID'].iloc[-1]
        last_id = int(last_id_str.split('-')[1])
    except Exception as e:
        print("Could not read existing CSV:", e)
        last_id = 0
        existing_df = None

    with open(raw_path, 'r', encoding='utf-8') as f:
        raw_text = f.read()

    # The new pattern: State and approval date on one line.
    # Ex: Odisha 03/2021
    pattern = re.compile(
        r'(?P<state>[A-Za-z\s&]+)\s+(?P<approval>\d{2}/\d{4}|NA|-)\s*\n\s*'
        r'\((?P<start>.*?)\)\s*\n\s*'
        r'(?P<target>\d{2}/\d{4}|-)\s*\n\s*'
        r'\((?P<revised_target>.*?)\)\s*\n\s*'
        r'(?P<orig_cost>[\d\.]+|-)\s*\n\s*'
        r'\((?P<rev_cost>[\d\.]+|-)\)\s*\n\s*'
        r'(?P<expenditure>[\d\.]+|-)\s+(?P<progress>[\d\.]+|-)'
    )
    
    projects = []
    ministries = ['Road Transport', 'Railways', 'Petroleum & Natural Gas', 'Power', 'Coal', 'Urban Affairs', 'Water Resources']
    
    matches = list(pattern.finditer(raw_text))
    print(f"Found {len(matches)} matches in raw_data_2.txt")
    
    # We will just append all matches found
    for match in matches:
        d = match.groupdict()
        
        orig_cost = float(d['orig_cost']) if d['orig_cost'] != '-' else 0.0
        rev_cost = float(d['rev_cost']) if d['rev_cost'] != '-' else orig_cost
        expenditure = float(d['expenditure']) if d['expenditure'] != '-' else 0.0
        progress = float(d['progress']) if d['progress'] != '-' else 0.0
        
        start_date_str = d['start']
        target_date_str = d['target']
        rev_target_str = d['revised_target']
        
        start_date = parse_date(start_date_str)
        target_date = parse_date(target_date_str)
        rev_target = parse_date(rev_target_str)
        
        if not start_date:
            start_date = datetime(2018, 1, 1)
        if not target_date:
            target_date = datetime(2022, 1, 1)
        if not rev_target:
            rev_target = target_date
            
        delay_months = max(0, (rev_target.year - target_date.year) * 12 + (rev_target.month - target_date.month))
        
        cost_overrun_pct = 0
        if orig_cost > 0:
            cost_overrun_pct = ((rev_cost - orig_cost) / orig_cost) * 100
            
        is_high_risk = int((delay_months > 6) or (cost_overrun_pct > 15))
        
        state = d['state'].strip()
        ministry = random.choice(ministries) # fallback random
        
        last_id += 1
        projects.append({
            'Project_ID': f'PRJ-{last_id:04d}',
            'Ministry': ministry,
            'State': state,
            'Original_Cost_Cr': round(orig_cost, 2),
            'Revised_Cost_Cr': round(rev_cost, 2),
            'Expenditure_Cr': round(expenditure, 2),
            'Physical_Progress_Pct': round(progress, 2),
            'Start_Date': start_date.strftime('%Y-%m-%d'),
            'Original_Target_Date': target_date.strftime('%Y-%m-%d'),
            'Revised_Target_Date': rev_target.strftime('%Y-%m-%d'),
            'Delay_Months': delay_months,
            'Cost_Overrun_Pct': round(cost_overrun_pct, 2),
            'Is_High_Risk': is_high_risk
        })
        
    if projects:
        new_df = pd.DataFrame(projects)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True) if existing_df is not None else new_df
        combined_df.to_csv(csv_path, index=False)
        print(f"Appended {len(projects)} new projects. Total records: {len(combined_df)}")
    else:
        print("No matches found to append.")

if __name__ == "__main__":
    main()
