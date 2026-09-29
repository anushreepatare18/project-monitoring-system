from app_db import SessionLocal, Project
import uuid
import random

db = SessionLocal()

def seed_data():
    if db.query(Project).count() > 0:
        print("Database already seeded.")
        return

    ministries = ["Ministry of Railways", "Ministry of Road Transport", "Ministry of Power"]
    sectors = ["Railways", "Highways", "Power Generation"]
    
    for i in range(10):
        original_cost = random.uniform(100.0, 1000.0)
        expenditure = original_cost * random.uniform(0.1, 1.2)
        physical_progress = random.uniform(5.0, 100.0)
        delay = random.uniform(0, 24)
        
        project = Project(
            id=f"PROJ-{str(uuid.uuid4())[:8].upper()}",
            name=f"Sample Project {i+1}",
            sector=random.choice(sectors),
            ministry=random.choice(ministries),
            implementing_agency=f"Agency {i % 3 + 1}",
            original_cost_cr=round(original_cost, 2),
            expenditure_cr=round(expenditure, 2),
            physical_progress_pct=round(physical_progress, 2),
            delay_months=round(delay, 2),
            cost_overrun_pct=round(max(0, (expenditure - original_cost) / original_cost * 100), 2)
        )
        db.add(project)
    
    db.commit()
    print("Database seeded with 10 projects.")

if __name__ == "__main__":
    seed_data()
