import sqlite3
from datetime import datetime, timedelta
import random

db_path = 'pragya.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all projects
cursor.execute("SELECT id, name, risk_level, delay_months, cost_overrun_pct FROM projects")
projects = cursor.fetchall()

# Clear existing alerts and updates for a clean slate
cursor.execute("DELETE FROM alerts")
try:
    cursor.execute("DELETE FROM project_history")
except sqlite3.OperationalError:
    pass
conn.commit()

now = datetime.utcnow()

for p in projects:
    p_id, name, risk_level, delay_months, cost_overrun_pct = p
    
    # Create Alerts for High/Critical Risk projects
    if risk_level in ['High', 'Critical']:
        alert_msg = ""
        if delay_months > 0:
            alert_msg += f"Significant delay of {delay_months} months. "
        if cost_overrun_pct > 0:
            alert_msg += f"Cost overrun of {cost_overrun_pct}%. "
        if not alert_msg:
            alert_msg = "Anomalous patterns detected by AI."
            
        # Create an alert
        cursor.execute("""
            INSERT INTO alerts (project_id, risk_score, message, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (p_id, 80.0 if risk_level == 'High' else 95.0, alert_msg, "New", now, now))
    
    # Randomly create pending updates (simulated as history records that are draft)
    # Actually, the frontend looks at project.updateStatus which is currently hardcoded in datasetService.ts
    # Let's just create alerts for now since that populates the alerts card.
    
conn.commit()
conn.close()

print("Successfully populated pragya.db with alerts based on the dataset.")
