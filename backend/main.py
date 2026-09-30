from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pickle
import pandas as pd
import numpy as np
import shap
import os
from sqlalchemy.orm import Session
from backend.app_db import SessionLocal, engine, Project, Alert, AuditLog, ProjectHistory
from typing import List, Optional
from datetime import datetime
import csv
import traceback
try:
    import google.generativeai as genai
    _GENAI_AVAILABLE = True
except ImportError:
    genai = None
    _GENAI_AVAILABLE = False

# Try loading GEMINI API KEY
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY and _GENAI_AVAILABLE:
    genai.configure(api_key=GEMINI_API_KEY)


app = FastAPI(title="PRAGYA AI Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to PRAGYA AI Backend API! Visit /docs for the interactive API dashboard."}

MODEL_PATH = "risk_model.pkl"
model = None
explainer = None

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Schemas
class ProjectUpdate(BaseModel):
    Original_Cost_Cr: float
    Expenditure_Cr: float
    Physical_Progress_Pct: float
    Financial_Progress_Pct: float = 0.0
    Delay_Months: float = 0.0
    Cost_Overrun_Pct: float = 0.0
    Reporting_Month: str = ""
    Submitted_By: str = ""
    Issues_Remarks: str = ""
    Milestones_Completed: str = ""

class ProjectSchema(BaseModel):
    id: str
    name: str
    sector: str
    ministry: str
    implementing_agency: str
    original_cost_cr: float
    expenditure_cr: float
    cost_overrun_pct: float
    delay_months: float
    physical_progress_pct: float
    status: str
    risk_score: float
    risk_level: str
    is_anomalous: bool
    
    class Config:
        orm_mode = True

class AlertReview(BaseModel):
    status: str # Verified, Dismissed
    officer_notes: Optional[str] = None
    user_role: str = "Officer"

from backend.ml_core.inference.infer import run_inference

# Mount the grounded chatbot router
try:
    from backend.chatbot.api import chatbot_router
    _chatbot_available = True
except Exception as _chatbot_err:
    print(f"[startup] Chatbot router not loaded: {_chatbot_err}")
    _chatbot_available = False

@app.on_event("startup")
async def load_model():
    # The inference engine is loaded on first call or we can pre-load it
    from backend.ml_core.inference.infer import get_inference_engine
    try:
        get_inference_engine()
        print("PRAGYA Inference Engine loaded successfully.")
    except Exception as e:
        print(f"Warning: Could not load inference engine: {e}")

    if _chatbot_available:
        app.include_router(chatbot_router)
        print("PRAGYA Chatbot router mounted at /chatbot")

@app.get("/api/health")
def health_check():
    return {"status": "ok", "model_loaded": model is not None}

@app.get("/api/projects", response_model=List[ProjectSchema])
def get_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    return projects

@app.get("/api/projects/{project_id}", response_model=ProjectSchema)
def get_project(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

def send_notification(project_id, risk_level):
    # Mocking FR-28: Multi-channel alert notifications
    print(f"[MOCK NOTIFICATION] Email sent to officers for Project {project_id} due to {risk_level} risk.")
    print(f"[MOCK NOTIFICATION] SMS sent to assigned officers for Project {project_id}.")

@app.post("/api/projects/{project_id}/update")
def update_project(project_id: str, data: ProjectUpdate, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    data_dict = data.dict() if hasattr(data, 'dict') else data.model_dump()

    # FR-VAL: Run validation
    from backend.validation import validate_project_update
    from backend.app_db import ValidationResult
    
    prev_state = {
        'original_cost_cr': project.original_cost_cr,
        'physical_progress_pct': project.physical_progress_pct,
    }
    val_result = validate_project_update(data_dict, prev_state)
    
    if not val_result["is_valid"]:
        raise HTTPException(status_code=400, detail={"errors": val_result["hard_errors"]})

    from backend.anomaly import detect_anomalies
    from backend.app_db import AnomalyResult
    
    anomaly_check = detect_anomalies(data_dict, prev_state)
    is_anomalous = anomaly_check["is_flagged"]
    
    # We still get risk_score from model
    data_dict['projectId'] = project.id
    data_dict['ministry'] = project.ministry
    data_dict['sector'] = project.sector
    data_dict['agency'] = project.implementing_agency
    
    risk_res = predict_risk_internal(data_dict)
    
    # Update project data
    project.expenditure_cr = data.Expenditure_Cr
    project.physical_progress_pct = data.Physical_Progress_Pct
    project.delay_months = data.Delay_Months
    project.cost_overrun_pct = data.Cost_Overrun_Pct
    project.risk_score = risk_res['risk_score']
    project.risk_level = risk_res['risk_level']
    project.is_anomalous = is_anomalous

    
    # Generate Alert if necessary using the new Alert Engine
    from backend.alert_engine import evaluate_alert_rules
    new_alert = evaluate_alert_rules(project, risk_res, is_anomalous, db)
    if new_alert:
        send_notification(project.id, risk_res['risk_level'])
    
    # Audit log
    audit = AuditLog(
        action="Project Update",
        user_role="Agency",
        details=f"Updated project {project.id} with progress {data.Physical_Progress_Pct}%"
    )
    db.add(audit)
    
    # Save project history (submitted data) to central DB for analysis
    history = ProjectHistory(
        project_id=project.id,
        submitted_by=data.Submitted_By,
        reporting_month=data.Reporting_Month,
        physical_progress_pct=data.Physical_Progress_Pct,
        financial_progress_pct=data.Financial_Progress_Pct,
        expenditure_cr=data.Expenditure_Cr,
        delay_months=data.Delay_Months,
        cost_overrun_pct=data.Cost_Overrun_Pct,
        issues_remarks=data.Issues_Remarks,
        milestones_completed=data.Milestones_Completed,
        risk_score=risk_res['risk_score'],
        risk_level=risk_res['risk_level'],
        is_anomalous=risk_res['is_anomalous']
    )
    db.add(history)
    db.flush() # To get history.id
    
    # Save Validation Results (Soft Warnings)
    for warning in val_result["soft_warnings"]:
        v_res = ValidationResult(
            update_id=history.id,
            rule_id="SW-01",
            severity="Soft warning",
            field=warning["field"],
            message=warning["message"]
        )
        db.add(v_res)
        
    # Save Anomaly Results
    import json
    anom_res = AnomalyResult(
        update_id=history.id,
        anomaly_score=anomaly_check["anomaly_score"],
        flagged=anomaly_check["is_flagged"],
        reasons_json=json.dumps(anomaly_check["reasons"])
    )
    db.add(anom_res)
    
    db.commit()
    
    # Append to dataset.csv to be utilized for analysis / retraining
    try:
        csv_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dataset.csv")
        update_date = datetime.now().strftime("%Y-%m-%d")
        new_row = [
            project.id, update_date, project.ministry, project.sector, project.implementing_agency, 
            "", project.original_cost_cr, "", "", "Infrastructure", 
            data.Physical_Progress_Pct, data.Financial_Progress_Pct, data.Expenditure_Cr, 
            project.original_cost_cr + (project.original_cost_cr * data.Cost_Overrun_Pct / 100) if project.original_cost_cr else 0,
            "", "", "", "", "", "", "", 1 if data.Delay_Months > 0 else 0, 1 if data.Cost_Overrun_Pct > 0 else 0, ""
        ]
        with open(csv_file_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(new_row)
    except Exception as e:
        print(f"Failed to append to dataset.csv: {e}")
    
    return {"status": "success", "risk_prediction": risk_res}

@app.post("/api/predict")
async def predict_risk(data: dict):
    return predict_risk_internal(data)

def predict_risk_internal(data: dict):
    # Construct a 1-row DataFrame mimicking the historical updates required by the pipeline
    import pandas as pd
    import traceback
    from datetime import datetime, timedelta

    # Use today as as_of, but set update_date to yesterday to cleanly
    # satisfy the pipeline's leakage check (update_date <= as_of, strict <)
    as_of = datetime.now().strftime("%Y-%m-%d")
    update_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    # Safely coerce dates — JS null arrives as Python None; also reject
    # non-date strings like "Not Available", "N/A", "TBD", etc.
    def safe_date(val, default):
        if not val:
            return default
        s = str(val).strip()
        if s.lower() in ('null', 'none', '', 'n/a', 'na', 'not available', 'tbd', 'unknown'):
            return default
        # Try actually parsing it — if pandas can't read it, use default
        try:
            import pandas as _pd
            _pd.to_datetime(s)
            return s
        except Exception:
            return default

    # Safely coerce numeric — JS undefined/null arrives as None
    def safe_num(val, default=0.0):
        try:
            return float(val) if val is not None else default
        except (TypeError, ValueError):
            return default

    start_date  = safe_date(data.get("startDate"), "2020-01-01")
    end_date    = safe_date(data.get("expectedCompletionDate"), "2027-12-31")
    sanctioned  = safe_num(data.get("Original_Cost_Cr"), 100.0) or 100.0
    expenditure = safe_num(data.get("Expenditure_Cr"), 0.0)
    phys_prog   = safe_num(data.get("Physical_Progress_Pct"), 0.0)
    fin_prog    = safe_num(data.get("financialProgress"), 0.0)
    revised     = safe_num(data.get("revisedCost"), sanctioned) or sanctioned

    # Ensure planned_end is always in the future relative to as_of
    # so the pipeline can compute velocity_needed_to_finish properly
    import pandas as pd_local
    try:
        planned_end_dt = pd_local.to_datetime(end_date)
        as_of_dt = pd_local.to_datetime(as_of)
        if planned_end_dt <= as_of_dt:
            # Project overdue — extend end date to 1 year from now for feature computation
            end_date = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
    except Exception:
        end_date = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")

    # Determine a sensible milestone planned date relative to start
    try:
        ms_planned = (pd_local.to_datetime(start_date) + pd_local.DateOffset(months=18)).strftime("%Y-%m-%d")
        ms_expected = (pd_local.to_datetime(start_date) + pd_local.DateOffset(months=24)).strftime("%Y-%m-%d")
    except Exception:
        ms_planned  = "2024-01-01"
        ms_expected = "2024-06-01"

    df = pd.DataFrame([{
        "project_id":               data.get("projectId", "PRJ-MOCK"),
        "update_date":              update_date,
        "ministry":                 data.get("ministry")  or "Ministry of Road Transport and Highways",
        "sector":                   data.get("sector")    or "Roads",
        "agency":                   data.get("agency")    or "NHAI",
        "state":                    data.get("state")     or "Delhi",
        "sanctioned_cost":          sanctioned,
        "planned_start":            start_date,
        "planned_end":              end_date,
        "project_type":             "Infrastructure",
        "physical_progress_pct":    phys_prog,
        "financial_progress_pct":   fin_prog,
        "cumulative_expenditure":   expenditure,
        "revised_cost":             revised,
        "expected_completion_date": end_date,
        "milestone_name":           "Milestone 1",
        "milestone_planned_date":   ms_planned,
        "milestone_expected_date":  ms_expected,
        "milestone_actual_date":    None
    }])

    try:
        res = run_inference(data.get("projectId", "PRJ-MOCK"), as_of, df)
    except Exception as e:
        print(f"[predict_risk_internal] Inference exception: {e}")
        traceback.print_exc()
        return {
            "risk_score": 50.0,
            "risk_level": "Medium",
            "is_anomalous": False,
            "alert_triggered": False,
            "shap_explanations": [],
            "error_detail": str(e)
        }

    if "error" in res:
        print(f"[predict_risk_internal] Inference returned error: {res['error']}")
        return {
            "risk_score": 50.0,
            "risk_level": "Medium",
            "is_anomalous": False,
            "alert_triggered": False,
            "shap_explanations": [],
            "error_detail": res["error"]
        }

    risk_score = res['composite_risk_score'] * 100

    # Filter out any error-dict entries from SHAP (in case SHAP partially failed)
    raw_shap = res.get('shap_explanation', [])
    valid_shap = [
        s for s in raw_shap
        if isinstance(s, dict) and 'feature' in s and 'impact' in s
    ]

    return {
        "risk_score":        round(risk_score, 2),
        "risk_level":        res['risk_band'],
        "is_anomalous":      res['anomaly_score'] > 0,
        "alert_triggered":   risk_score > 75,
        "shap_explanations": valid_shap,
        "p_cost":            res.get('p_cost', 0),
        "p_time":            res.get('p_time', 0),
        "p_impl":            res.get('p_impl', 0),
    }

@app.get("/api/alerts")
def get_alerts(db: Session = Depends(get_db)):
    alerts = db.query(Alert).all()
    # join with project to get project name
    result = []
    for a in alerts:
        p = db.query(Project).filter(Project.id == a.project_id).first()
        result.append({
            "id": a.id,
            "project_id": a.project_id,
            "project_name": p.name if p else "Unknown",
            "risk_score": a.risk_score,
            "message": a.message,
            "status": a.status,
            "officer_notes": a.officer_notes,
            "created_at": a.created_at
        })
    return result

@app.post("/api/alerts/{alert_id}/review")
def review_alert(alert_id: int, review: AlertReview, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    alert.status = review.status
    alert.officer_notes = review.officer_notes
    
    # Audit log
    audit = AuditLog(
        action="Alert Review",
        user_role=review.user_role,
        details=f"Reviewed alert {alert.id}. Status: {review.status}"
    )
    db.add(audit)
    db.commit()
    return {"status": "success"}

@app.get("/api/audit")
def get_audit_logs(db: Session = Depends(get_db)):
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(100).all()
    return logs

@app.get("/api/projects/{project_id}/explanation")
def get_project_explanation(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    # We use the current project state to generate explanation
    data = ProjectUpdate(
        Original_Cost_Cr=project.original_cost_cr,
        Expenditure_Cr=project.expenditure_cr,
        Physical_Progress_Pct=project.physical_progress_pct,
        Delay_Months=project.delay_months,
        Cost_Overrun_Pct=project.cost_overrun_pct
    )
    risk_res = predict_risk_internal(data)
    
    return {
        "project_id": project.id,
        "risk_score": risk_res['risk_score'],
        "shap_explanations": risk_res['shap_explanations']
    }

@app.get("/api/projects/{project_id}/benchmark")
def get_project_benchmark(project_id: str, db: Session = Depends(get_db)):
    from backend.analytics import compute_project_benchmarks
    from datetime import datetime
    
    result = compute_project_benchmarks(project_id, datetime.utcnow(), db)
    if not result:
        raise HTTPException(status_code=404, detail="Project or peers not found")
        
    db.commit() # Save the benchmark result log
    return result

@app.get("/api/portfolio/summary")
def get_portfolio_summary(db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    total = len(projects)
    
    bands = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    for p in projects:
        bands[p.risk_level] = bands.get(p.risk_level, 0) + 1
        
    return {
        "total_projects": total,
        "risk_distribution": bands,
        "total_cost": sum(p.original_cost_cr for p in projects),
        "total_expenditure": sum(p.expenditure_cr for p in projects)
    }

@app.get("/api/portfolio/sectors")
def get_portfolio_sectors(db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    
    sectors = {}
    for p in projects:
        if p.sector not in sectors:
            sectors[p.sector] = {"count": 0, "avg_risk": 0.0, "total_cost": 0.0}
        sectors[p.sector]["count"] += 1
        sectors[p.sector]["avg_risk"] += p.risk_score
        sectors[p.sector]["total_cost"] += p.original_cost_cr
        
    for s in sectors:
        sectors[s]["avg_risk"] /= sectors[s]["count"]
        
    return sectors
@app.get("/api/anomalies")
def get_anomalies(db: Session = Depends(get_db)):
    # Return projects that are flagged as anomalous
    projects = db.query(Project).filter(Project.is_anomalous == True).all()
    
    anomalies = []
    for p in projects:
        anomalies.append({
            "project_id": p.id,
            "project_name": p.name,
            "agency": p.implementing_agency,
            "anomaly_score": p.risk_score, # using risk score as proxy for prototype
            "reasons": ["Progress is 30% below expected", "Unusual expenditure rate"],
            "status": "Flagged"
        })
    return anomalies

@app.get("/api/public/projects")
def get_public_projects(db: Session = Depends(get_db)):
    # FR-16: Display only approved, releasable project information to public users
    # We simulate this by returning only a subset of fields and filtering by some criteria 
    # (for the prototype we will return all projects but strip out sensitive ML metrics)
    projects = db.query(Project).all()
    public_projects = []
    for p in projects:
        public_projects.append({
            "project_id": p.id,
            "project_name": p.name,
            "sector": p.sector,
            "ministry": p.ministry,
            "agency": p.implementing_agency,
            "approved_cost": p.original_cost_cr,
            "expenditure": p.expenditure_cr,
            "physical_progress": p.physical_progress_pct,
            "status": p.status
        })
    return public_projects

@app.get("/api/analytics/drivers")
def get_analytics_drivers(db: Session = Depends(get_db)):
    # FR-12 Cost Escalation Analysis: Analyze factors associated with cost growth
    from backend.analytics import get_cost_escalation_drivers
    return get_cost_escalation_drivers(db)

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/api/auth/login")
def login(req: LoginRequest):
    # Mock authentication for prototype
    if req.username == "admin" and req.password == "admin":
        return {"token": "mock-admin-token", "role": "Admin", "name": "System Admin"}
    elif req.username.startswith("officer"):
        return {"token": "mock-officer-token", "role": "Monitoring Officer", "name": "Review Officer"}
    elif req.username.startswith("agency"):
        return {"token": "mock-agency-token", "role": "Agency", "name": "Agency Nodal"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")



class DatasetChatRequest(BaseModel):
    query: str
    history: Optional[List[dict]] = []

@app.post("/api/chat/dataset")
def chat_dataset(req: DatasetChatRequest):
    if not GEMINI_API_KEY:
        return {"reply": "Warning: Gemini API Key is not set in the backend environment. Please set GEMINI_API_KEY to enable LLM features."}
    
    try:
        dataset_path = "project_data.csv"
        dataset_content = ""
        if os.path.exists(dataset_path):
            with open(dataset_path, "r", encoding="utf-8") as f:
                dataset_content = f.read()
        else:
            return {"reply": "Warning: Dataset file not found."}
            
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Build prompt
        history_text = ""
        if req.history:
            history_text = "Chat History:\n"
            for msg in req.history:
                history_text += f"{msg['role'].capitalize()}: {msg['text']}\n"
            history_text += "\n"

        prompt = f"""
You are PRAGYA AI, a highly capable project intelligence assistant. 
You have been provided with the following comprehensive dataset of infrastructure projects:
<dataset>
{dataset_content}
</dataset>

Please use ONLY this dataset to answer the user's questions. 
If the user asks something that cannot be answered using this dataset, politely explain that you don't have that information.
Keep your answers clear, concise, and structured.

{history_text}User's Query:
"{req.query}"
"""
        response = model.generate_content(prompt)
        return {"reply": response.text}
    except Exception as e:
        return {"reply": f"An error occurred while generating the response: {str(e)}"}

