from sqlalchemy.orm import Session
from datetime import datetime
from backend.app_db import Alert

def evaluate_alert_rules(project, risk_res: dict, is_anomalous: bool, db: Session):
    """
    Evaluates early warning rules according to SRS 5.12.
    Creates or updates alerts based on risk score and anomaly flags.
    """
    trigger_type = None
    severity = "Medium"
    message = ""
    
    # Trigger A: Risk Score crossed band threshold upward
    if risk_res['risk_score'] >= 80:
        trigger_type = "critical_risk"
        severity = "Critical"
        message = "Project has entered Critical Risk band based on cost and schedule drivers."
    elif risk_res['risk_score'] >= 60:
        trigger_type = "high_risk"
        severity = "High"
        message = "High Schedule/Cost Risk predicted."
        
    # Trigger D: Anomaly flagged
    if is_anomalous and not trigger_type:
        trigger_type = "anomaly_flagged"
        severity = "Medium"
        message = "Anomalous update detected. Verification required."
        
    if trigger_type:
        # Check for open duplicate alerts
        existing = db.query(Alert).filter(
            Alert.project_id == project.id,
            Alert.trigger_type == trigger_type,
            Alert.status == "Open"
        ).first()
        
        if not existing:
            new_alert = Alert(
                project_id=project.id,
                trigger_type=trigger_type,
                severity=severity,
                risk_score=risk_res['risk_score'],
                message=message,
                status="Open",
                created_at=datetime.utcnow()
            )
            db.add(new_alert)
            return new_alert
            
    return None
