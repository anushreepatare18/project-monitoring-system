import pdfplumber
import pandas as pd
import re
from datetime import datetime
import os

pdf_path = r"C:\Users\RAMESH PATARE\.gemini\antigravity-ide\brain\11d61273-8afa-4509-bfa6-4728451f43e7\.user_uploaded\media_1790751918248.pdf"

def parse_date(d_str):
    if not d_str or d_str in ['-', 'NA', 'None', '']:
        return None
    try:
        return datetime.strptime(d_str.strip(), '%m/%Y')
    except:
        return None

def extract_data_from_pdf(pdf_path):
    projects = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                if not table or len(table) < 2:
                    continue
                header = [str(x).replace('\n', ' ') if x else '' for x in table[0]]
                if 'Sl.No' not in header or 'State' not in header:
                    continue
                
                # It's a valid data table
                for row in table[1:]:
                    if len(row) < 7:
                        continue
                    
                    # Columns usually: Sl.No, Project Name, State, Date of Approval, Orignal/Target DoC, Orignal Cost, Cumulative Exp, Physical Progress
                    sl_no = row[0]
                    if not sl_no or not str(sl_no).strip().isdigit():
                        continue
                        
                    project_name_cell = str(row[1] or '')
                    state = str(row[2] or '').strip().replace('\n', ' ')
                    
                    dates_cell = str(row[3] or '')
                    target_cell = str(row[4] or '')
                    cost_cell = str(row[5] or '')
                    exp_cell = str(row[6] or '')
                    progress_cell = str(row[7] or '0') if len(row) > 7 else '0'
                    
                    # Extract Project Name, Agency, Ministry etc.
                    project_name = project_name_cell.split('\n(')[0].strip()
                    agency_match = re.search(r'\((.*?)\)', project_name_cell)
                    agency = agency_match.group(1) if agency_match else 'Unknown Agency'
                    ministry = "Central Sector" # Can be refined later based on headers
                    
                    # Dates: mm/yyyy
                    start_dates = re.findall(r'\d{2}/\d{4}', dates_cell)
                    target_dates = re.findall(r'\d{2}/\d{4}', target_cell)
                    
                    start_date = parse_date(start_dates[0]) if start_dates else datetime(2018, 1, 1)
                    target_date = parse_date(target_dates[0]) if target_dates else datetime(2022, 1, 1)
                    rev_target = parse_date(target_dates[-1]) if target_dates else target_date
                    
                    # Costs
                    costs = re.findall(r'[\d\.]+', cost_cell)
                    orig_cost = float(costs[0]) if costs else 0.0
                    rev_cost = float(costs[-1]) if costs else orig_cost
                    
                    expenditures = re.findall(r'[\d\.]+', exp_cell)
                    expenditure = float(expenditures[0]) if expenditures else 0.0
                    
                    progresses = re.findall(r'[\d\.]+', progress_cell)
                    progress = float(progresses[0]) if progresses else 0.0
                    
                    delay_months = max(0, (rev_target.year - target_date.year) * 12 + (rev_target.month - target_date.month))
                    cost_overrun_pct = ((rev_cost - orig_cost) / orig_cost * 100) if orig_cost > 0 else 0
                    is_high_risk = int(delay_months > 6 or cost_overrun_pct > 15)
                    
                    projects.append({
                        'project_id': f'PRJ-{int(sl_no):04d}',
                        'ministry': ministry,
                        'sector': 'Infrastructure',
                        'agency': agency,
                        'state': state,
                        'sanctioned_cost': round(orig_cost, 2),
                        'revised_cost': round(rev_cost, 2),
                        'cumulative_expenditure': round(expenditure, 2),
                        'physical_progress_pct': round(progress, 2),
                        'planned_start': start_date.strftime('%Y-%m-%d'),
                        'planned_end': target_date.strftime('%Y-%m-%d'),
                        'expected_completion_date': rev_target.strftime('%Y-%m-%d'),
                        'max_milestone_delay_months': delay_months,
                        'cost_growth_pct': round(cost_overrun_pct, 2),
                        'delayed_flag': 1 if delay_months > 0 else 0,
                        'overrun_flag': 1 if cost_overrun_pct > 0 else 0,
                        'label_overrun': 1 if cost_overrun_pct > 0 else 0,
                        'label_delay': 1 if delay_months > 0 else 0,
                        'label_impl_risk': is_high_risk,
                        # Required by some systems
                        'update_date': datetime.now().strftime('%Y-%m-%d')
                    })
                    
    return projects

def main():
    print("Extracting data from PDF...")
    data = extract_data_from_pdf(pdf_path)
    if data:
        df = pd.DataFrame(data)
        df.to_csv("dataset.csv", index=False)
        print(f"Extracted {len(data)} projects and saved to dataset.csv")
    else:
        print("No data extracted.")

if __name__ == "__main__":
    main()
