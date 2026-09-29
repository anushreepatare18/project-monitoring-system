import pandas as pd
import numpy as np

# Real data extracted from the Flash Reports provided by the user
data = [
    {
        "Project_ID": "612786",
        "Name": "Construction of New Domestic Terminal Building Kadapa Airport",
        "Ministry": "Aviation",
        "State": "Andhra Pradesh",
        "Original_Cost_Cr": 265.91,
        "Revised_Cost_Cr": 265.91,
        "Expenditure_Cr": 129.07,
        "Physical_Progress_Pct": 65.0,
        "Start_Date": "2023-03-01",
        "Target_Date": "2026-01-01"
    },
    {
        "Project_ID": "701107",
        "Name": "New Integrated Terminal Building Vijayawada Airport",
        "Ministry": "Aviation",
        "State": "Andhra Pradesh",
        "Original_Cost_Cr": 611.80,
        "Revised_Cost_Cr": 611.80,
        "Expenditure_Cr": 523.14,
        "Physical_Progress_Pct": 87.2,
        "Start_Date": "2020-06-01",
        "Target_Date": "2026-11-01"
    },
    {
        "Project_ID": "706724",
        "Name": "Guwahati Airport New Integrated Terminal",
        "Ministry": "Aviation",
        "State": "Assam",
        "Original_Cost_Cr": 1712.00,
        "Revised_Cost_Cr": 2520.00,
        "Expenditure_Cr": 2627.39,
        "Physical_Progress_Pct": 98.0,
        "Start_Date": "2016-12-01",
        "Target_Date": "2026-06-01"
    },
    {
        "Project_ID": "400120",
        "Name": "KG-DWN-98/2 Cluster - II Development Project",
        "Ministry": "Petroleum & Natural Gas",
        "State": "Andhra Pradesh",
        "Original_Cost_Cr": 34012.00,
        "Revised_Cost_Cr": 34012.00,
        "Expenditure_Cr": 33006.7,
        "Physical_Progress_Pct": 96.5,
        "Start_Date": "2016-03-01",
        "Target_Date": "2026-09-01"
    },
    {
        "Project_ID": "619226",
        "Name": "Provision of four bitumen tanks at Visakh Refinery",
        "Ministry": "Petroleum & Natural Gas",
        "State": "Andhra Pradesh",
        "Original_Cost_Cr": 258.34,
        "Revised_Cost_Cr": 258.34,
        "Expenditure_Cr": 1.65,
        "Physical_Progress_Pct": 10.5,
        "Start_Date": "2025-09-01",
        "Target_Date": "2028-03-01"
    },
    {
        "Project_ID": "709798",
        "Name": "Ethylene Cracker Project at Bina Refinery",
        "Ministry": "Petroleum & Natural Gas",
        "State": "Madhya Pradesh",
        "Original_Cost_Cr": 43367.00,
        "Revised_Cost_Cr": 43367.00,
        "Expenditure_Cr": 4802.7,
        "Physical_Progress_Pct": 25.5,
        "Start_Date": "2023-05-01",
        "Target_Date": "2028-05-01"
    },
    {
        "Project_ID": "617183",
        "Name": "Transmission system strengthening at Kurnool",
        "Ministry": "Power",
        "State": "Andhra Pradesh",
        "Original_Cost_Cr": 2886.00,
        "Revised_Cost_Cr": 2886.00,
        "Expenditure_Cr": 721.48,
        "Physical_Progress_Pct": 26.19,
        "Start_Date": "2025-03-01",
        "Target_Date": "2027-12-01"
    },
    {
        "Project_ID": "400426",
        "Name": "Expansion of Malanjkhand Copper Project",
        "Ministry": "Mines",
        "State": "Madhya Pradesh",
        "Original_Cost_Cr": 1856.36,
        "Revised_Cost_Cr": 3800.00,
        "Expenditure_Cr": 965.07,
        "Physical_Progress_Pct": 84.87,
        "Start_Date": "2011-09-01",
        "Target_Date": "2029-03-01"
    },
    {
        "Project_ID": "400141",
        "Name": "Expansion of Alumina Refinery Plant NALCO",
        "Ministry": "Mines",
        "State": "Odisha",
        "Original_Cost_Cr": 4103.00,
        "Revised_Cost_Cr": 5677.40,
        "Expenditure_Cr": 4887.6,
        "Physical_Progress_Pct": 94.2,
        "Start_Date": "2017-04-01",
        "Target_Date": "2026-06-01"
    },
    {
        "Project_ID": "618630",
        "Name": "6L of MH/KN Border Nimbal Village",
        "Ministry": "Road Transport",
        "State": "Karnataka",
        "Original_Cost_Cr": 2355.56,
        "Revised_Cost_Cr": 1923.3,
        "Expenditure_Cr": 868.81,
        "Physical_Progress_Pct": 76.12,
        "Start_Date": "2022-02-01",
        "Target_Date": "2026-11-01"
    },
    {
        "Project_ID": "705728",
        "Name": "MUMBAI-AHMEDABAD HIGH SPEED RAIL PROJECT- 508 KM",
        "Ministry": "Railways",
        "State": "Maharashtra",
        "Original_Cost_Cr": 108000.00,
        "Revised_Cost_Cr": 108000.00,
        "Expenditure_Cr": 90967.00,
        "Physical_Progress_Pct": 60.87,
        "Start_Date": "2018-01-01",
        "Target_Date": "2028-12-01"
    },
    {
        "Project_ID": "702668",
        "Name": "CHENNAI METRO RAIL PHASE-II DEVELOPMENT PROJECT",
        "Ministry": "Housing & Urban Affairs",
        "State": "Tamil Nadu",
        "Original_Cost_Cr": 63246.00,
        "Revised_Cost_Cr": 63246.00,
        "Expenditure_Cr": 33774.00,
        "Physical_Progress_Pct": 53.36,
        "Start_Date": "2021-01-01",
        "Target_Date": "2027-12-01"
    },
    {
        "Project_ID": "705237",
        "Name": "WESTERN DEDICATED FREIGHT CORRIDOR",
        "Ministry": "Railways",
        "State": "Multi-States",
        "Original_Cost_Cr": 51101.00,
        "Revised_Cost_Cr": 124005.00,
        "Expenditure_Cr": 124623.00,
        "Physical_Progress_Pct": 96.0,
        "Start_Date": "2010-01-01",
        "Target_Date": "2026-12-01"
    },
    {
        "Project_ID": "706780",
        "Name": "MUMBAI URBAN TRANSPORT PROJECT [MUTP] PHASE-IIIA",
        "Ministry": "Railways",
        "State": "Maharashtra",
        "Original_Cost_Cr": 33690.00,
        "Revised_Cost_Cr": 33690.00,
        "Expenditure_Cr": 3854.00,
        "Physical_Progress_Pct": 25.0,
        "Start_Date": "2019-01-01",
        "Target_Date": "2029-12-01"
    },
    {
        "Project_ID": "701289",
        "Name": "CAPACITY EXPANSION OF PANIPAT REFINERY FROM 15 TO 25 MMTPA",
        "Ministry": "Petroleum & Natural Gas",
        "State": "Haryana",
        "Original_Cost_Cr": 34627.00,
        "Revised_Cost_Cr": 36225.00,
        "Expenditure_Cr": 27518.00,
        "Physical_Progress_Pct": 94.0,
        "Start_Date": "2021-02-01",
        "Target_Date": "2026-12-01"
    },
    {
        "Project_ID": "602182",
        "Name": "DIBANG MULTIPURPOSE PROJECT",
        "Ministry": "Power",
        "State": "Arunachal Pradesh",
        "Original_Cost_Cr": 31876.00,
        "Revised_Cost_Cr": 31876.00,
        "Expenditure_Cr": 4750.00,
        "Physical_Progress_Pct": 17.78,
        "Start_Date": "2023-02-01",
        "Target_Date": "2032-02-01"
    },
    {
        "Project_ID": "701415",
        "Name": "POLAVARAM IRRIGATION PROJECT",
        "Ministry": "Water Resources",
        "State": "Andhra Pradesh",
        "Original_Cost_Cr": 10151.00,
        "Revised_Cost_Cr": 55549.00,
        "Expenditure_Cr": 27726.00,
        "Physical_Progress_Pct": 86.14,
        "Start_Date": "2009-01-01",
        "Target_Date": "2026-03-01"
    },
    {
        "Project_ID": "706775",
        "Name": "BHARATNET",
        "Ministry": "Telecommunications",
        "State": "Multi-States",
        "Original_Cost_Cr": 61109.00,
        "Revised_Cost_Cr": 188000.00,
        "Expenditure_Cr": 48810.00,
        "Physical_Progress_Pct": 99.98,
        "Start_Date": "2017-07-01",
        "Target_Date": "2027-03-01"
    },
    {
        "Project_ID": "400188",
        "Name": "REDEVELOPMENT OF SEVEN GENERAL POOL RESIDENTIAL ACCOMMODATION",
        "Ministry": "Housing & Urban Affairs",
        "State": "Delhi",
        "Original_Cost_Cr": 32850.00,
        "Revised_Cost_Cr": 32841.00,
        "Expenditure_Cr": 14370.00,
        "Physical_Progress_Pct": 46.7,
        "Start_Date": "2016-07-01",
        "Target_Date": "2025-12-01"
    }
]

df = pd.DataFrame(data)

# Add derived columns required by the model
df['Delay_Months'] = 0.0 # simplified for mock
df['Cost_Overrun_Pct'] = ((df['Revised_Cost_Cr'] - df['Original_Cost_Cr']) / df['Original_Cost_Cr']) * 100
df['Cost_Overrun_Pct'] = df['Cost_Overrun_Pct'].fillna(0)

# Target variable for training
df['Is_High_Risk'] = ((df['Cost_Overrun_Pct'] > 10) | (df['Physical_Progress_Pct'] < 40)).astype(int)

# In order to train a robust model, we will augment this real data with our previous synthetic data generator
# to have enough samples for XGBoost to learn properly, but we will seed the real data first.

synthetic_df = pd.read_csv('project_data.csv')
combined_df = pd.concat([df, synthetic_df], ignore_index=True)

# Keep the columns we need
final_columns = ['Project_ID', 'Name', 'Ministry', 'State', 'Original_Cost_Cr', 'Expenditure_Cr', 'Physical_Progress_Pct', 'Delay_Months', 'Cost_Overrun_Pct', 'Is_High_Risk']

# Clean up synthetic data missing columns and merge properly
for col in final_columns:
    if col not in combined_df.columns:
        combined_df[col] = "Unknown" if col in ['Project_ID', 'Name'] else 0

combined_df = combined_df[final_columns]
combined_df.to_csv('project_data.csv', index=False)
print("Real PDF data successfully merged into project_data.csv!")
