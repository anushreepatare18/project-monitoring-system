import pandas as pd
from sqlalchemy.orm import Session
import sys
import os

# Ensure backend can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.app_db import engine, Project

def seed():
    print("Reading dataset.csv...")
    df = pd.read_csv("dataset.csv")
    
    # Sort by project_id and update_date, and keep the latest update for each project
    df['update_date'] = pd.to_datetime(df['update_date'])
    df = df.sort_values(['project_id', 'update_date'])
    latest_df = df.drop_duplicates(subset=['project_id'], keep='last')
    
    with Session(engine) as session:
        # Clear existing demo projects
        session.query(Project).delete()
        
        projects = []
        for _, row in latest_df.iterrows():
            # Derive risk level based on overrun and delay for prototype
            risk_score = 0.0
            if row['delayed_flag'] == 1: risk_score += 40
            if row['overrun_flag'] == 1: risk_score += 40
            if pd.notnull(row['physical_progress_pct']) and pd.notnull(row['financial_progress_pct']):
                if row['financial_progress_pct'] > row['physical_progress_pct'] + 20:
                    risk_score += 20
            
            risk_level = "Low"
            if risk_score >= 75: risk_level = "Critical"
            elif risk_score >= 50: risk_level = "High"
            elif risk_score >= 25: risk_level = "Medium"

            # Calculate cost overrun %
            rev_cost = row['revised_cost'] if pd.notnull(row['revised_cost']) else row['sanctioned_cost']
            sanc_cost = row['sanctioned_cost'] if pd.notnull(row['sanctioned_cost']) else 0
            cost_overrun_pct = 0.0
            if sanc_cost > 0:
                cost_overrun_pct = max(0, ((rev_cost - sanc_cost) / sanc_cost) * 100)

            project = Project(
                id=str(row['project_id']),
                name=f"Infrastructure Project {row['project_id']}", 
                sector=str(row['sector']),
                ministry=str(row['ministry']),
                implementing_agency=str(row['agency']),
                original_cost_cr=float(row['sanctioned_cost']) if pd.notnull(row['sanctioned_cost']) else 0.0,
                expenditure_cr=float(row['cumulative_expenditure']) if pd.notnull(row['cumulative_expenditure']) else 0.0,
                cost_overrun_pct=float(cost_overrun_pct),
                delay_months=float(12.0) if row['delayed_flag'] == 1 else 0.0, # Placeholder mock
                physical_progress_pct=float(row['physical_progress_pct']) if pd.notnull(row['physical_progress_pct']) else 0.0,
                status="Ongoing",
                risk_score=float(risk_score),
                risk_level=risk_level,
                is_anomalous=(row['financial_progress_pct'] > row['physical_progress_pct'] + 20) if pd.notnull(row['physical_progress_pct']) and pd.notnull(row['financial_progress_pct']) else False
            )
            projects.append(project)
        
        session.add_all(projects)
        session.commit()
        print(f"Successfully seeded {len(projects)} projects from dataset.csv.")

if __name__ == "__main__":
    seed()
