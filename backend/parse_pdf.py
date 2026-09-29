import pdfplumber
import pandas as pd
import re
import os

pdf_dir = r"C:\Users\RAMESH PATARE\OneDrive\Desktop\SIH\SIH26103\dataset"
csv_path = r"C:\Users\RAMESH PATARE\OneDrive\Desktop\SIH\SIH26103\public\data\project_data.csv"

all_data = []

def get_month_index(filename):
    months = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
    name = filename.lower()
    for i, m in enumerate(months):
        if m in name:
            return i
    return 0

# Get all PDFs and sort them chronologically by month
pdf_files = sorted([f for f in os.listdir(pdf_dir) if f.endswith('.pdf')], key=get_month_index)

for pdf_file in pdf_files:
    pdf_path = os.path.join(pdf_dir, pdf_file)
    print(f"Parsing {pdf_file}...")
    
    with pdfplumber.open(pdf_path) as pdf:
        for i in range(len(pdf.pages)):
            page = pdf.pages[i]
            table = page.extract_table()
            if table:
                for row in table:
                    if not row or not row[0]: continue
                    if len(row) < 8: continue
                    sl_no = str(row[0]).replace('\n', '').strip()
                    if not sl_no.isdigit():
                        continue
                    
                    project_info = str(row[1])
                    lines = project_info.split('\n')
                    name = lines[0].strip() if lines else ""
                    
                    project_id = sl_no
                    # look for (xxxxxx) where x is digit
                    matches = re.findall(r'\((\d{6})\)', project_info)
                    if matches:
                        project_id = matches[0]
                    
                    state = str(row[2]).replace('\n', ' ').strip()
                    
                    # Column 5: Orignal Cost \n (Revised Cost)
                    cost_str = str(row[5]).split('\n')[0].strip()
                    try:
                        original_cost_cr = float(cost_str)
                    except:
                        original_cost_cr = 0.0
                        
                    # Column 6: Cumulative Expenditure
                    exp_str = str(row[6]).replace('\n', '').strip()
                    try:
                        expenditure_cr = float(exp_str)
                    except:
                        expenditure_cr = 0.0
                        
                    # Column 7: Physical Progress
                    prog_str = str(row[7]).replace('\n', '').strip()
                    try:
                        physical_progress_pct = float(prog_str)
                    except:
                        physical_progress_pct = 0.0
                        
                    # Derive ministry
                    ministry = "Infrastructure"
                    if "NHAI" in project_info or "MoRTH" in project_info or "NHIDCL" in project_info or "Road" in project_info or "Highway" in project_info:
                        ministry = "Road Transport & Highways"
                    elif "Railway" in project_info or "Rail" in project_info or "RVNL" in project_info or "IRCON" in project_info:
                        ministry = "Railways"
                    elif "Petroleum" in project_info or "Oil" in project_info or "Gas" in project_info or "ONGC" in project_info or "IOCL" in project_info or "BPCL" in project_info or "HPCL" in project_info:
                        ministry = "Petroleum & Natural Gas"
                    elif "Power" in project_info or "NTPC" in project_info or "Thermal" in project_info or "NHPC" in project_info or "SJVN" in project_info or "POWERGRID" in project_info:
                        ministry = "Power"
                    elif "Water" in project_info or "Irrigation" in project_info or "Ganga" in project_info:
                        ministry = "Water Resources"
                    elif "Urban" in project_info or "Metro" in project_info or "NBCC" in project_info or "CPWD" in project_info:
                        ministry = "Housing & Urban Affairs"
                    elif "Coal" in project_info or "SECL" in project_info or "WCL" in project_info or "NCL" in project_info or "CCL" in project_info or "BCCL" in project_info or "MCL" in project_info or "ECL" in project_info or "NLCIL" in project_info:
                        ministry = "Coal"
                    elif "Telecommunications" in project_info or "BSNL" in project_info or "DoT" in project_info:
                        ministry = "Telecommunications"
                    elif "Aviation" in project_info or "Airport" in project_info or "AAI" in project_info:
                        ministry = "Aviation"
                    elif "Mines" in project_info or "NALCO" in project_info or "HCL" in project_info or "NMDC" in project_info:
                        ministry = "Mines"
                    elif "Steel" in project_info or "SAIL" in project_info:
                        ministry = "Steel"
                    elif "Health" in project_info or "AIIMS" in project_info or "Hospital" in project_info:
                        ministry = "Health"
                    elif "Education" in project_info or "IIT" in project_info or "NIT" in project_info:
                        ministry = "Education"
                        
                    delay_months = 0.0
                    cost_overrun_pct = 0.0
                    is_high_risk = 0
                    
                    cost_lines = str(row[5]).split('\n')
                    if len(cost_lines) > 1:
                        try:
                            revised_cost_cr = float(cost_lines[1].strip().replace('(', '').replace(')', ''))
                            if original_cost_cr > 0 and revised_cost_cr > original_cost_cr:
                                cost_overrun_pct = round(((revised_cost_cr - original_cost_cr) / original_cost_cr) * 100, 2)
                                if cost_overrun_pct > 10:
                                    is_high_risk = 1
                        except:
                            pass
    
                    if physical_progress_pct < 50 and expenditure_cr > (0.6 * original_cost_cr) and original_cost_cr > 0:
                        is_high_risk = 1
                    
                    all_data.append({
                        "Project_ID": project_id,
                        "Name": name.replace(',', ' '),
                        "Ministry": ministry,
                        "State": state,
                        "Original_Cost_Cr": original_cost_cr,
                        "Expenditure_Cr": expenditure_cr,
                        "Physical_Progress_Pct": physical_progress_pct,
                        "Delay_Months": delay_months,
                        "Cost_Overrun_Pct": cost_overrun_pct,
                        "Is_High_Risk": is_high_risk,
                        "Source_File": pdf_file
                    })

df = pd.DataFrame(all_data)
# Filter out empty names or invalid rows if any
df = df[df['Name'] != ""]

# Since we sorted PDFs by month chronologically, keeping 'last' keeps the most recent month's data
df = df.drop_duplicates(subset=['Project_ID'], keep='last')

df.to_csv(csv_path, index=False)
print(f"Successfully extracted {len(df)} unique projects and saved to {csv_path}")
