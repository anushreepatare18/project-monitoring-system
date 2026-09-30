from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./backend/pragya.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Project(Base):
    __tablename__ = "projects"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    sector = Column(String, index=True)
    ministry = Column(String, index=True)
    implementing_agency = Column(String)
    state = Column(String, nullable=True)
    district = Column(String, nullable=True)
    
    # Financials
    original_cost_cr = Column(Float, default=0.0)
    expenditure_cr = Column(Float, default=0.0)
    cost_overrun_pct = Column(Float, default=0.0)
    sanction_date = Column(DateTime, nullable=True)
    
    # Schedule
    planned_start = Column(DateTime, nullable=True)
    planned_end = Column(DateTime, nullable=True)
    delay_months = Column(Float, default=0.0)
    physical_progress_pct = Column(Float, default=0.0)
    status = Column(String, default="Ongoing")
    project_type = Column(String, default="Infrastructure")
    public_approved_flag = Column(Boolean, default=False)
    
    # Risk
    risk_score = Column(Float, default=0.0)
    risk_level = Column(String, default="Low")
    is_anomalous = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    alerts = relationship("Alert", back_populates="project")
    milestones = relationship("Milestone", back_populates="project")

class Milestone(Base):
    __tablename__ = "milestones"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(String, ForeignKey("projects.id"))
    name = Column(String)
    planned_date = Column(DateTime, nullable=True)
    expected_date = Column(DateTime, nullable=True)
    actual_date = Column(DateTime, nullable=True)
    weight_pct = Column(Float, default=0.0)
    status = Column(String, default="Pending")
    
    project = relationship("Project", back_populates="milestones")

class ProjectHistory(Base):
    __tablename__ = "project_history"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(String, ForeignKey("projects.id"))
    submitted_by = Column(String)
    reporting_month = Column(String)
    physical_progress_pct = Column(Float)
    financial_progress_pct = Column(Float)
    expenditure_cr = Column(Float)
    delay_months = Column(Float, default=0.0)
    cost_overrun_pct = Column(Float, default=0.0)
    issues_remarks = Column(Text, nullable=True)
    milestones_completed = Column(Text, nullable=True)
    risk_score = Column(Float, default=0.0)
    risk_level = Column(String, default="Low")
    is_anomalous = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

class ValidationResult(Base):
    __tablename__ = "validation_results"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    update_id = Column(Integer, ForeignKey("project_history.id"))
    rule_id = Column(String)
    severity = Column(String) # Hard error, Soft warning
    field = Column(String)
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(String, ForeignKey("projects.id"))
    prediction_id = Column(String, nullable=True)
    trigger_type = Column(String, nullable=True)
    severity = Column(String, default="High")
    risk_score = Column(Float)
    message = Column(Text)
    status = Column(String, default="Open") # Open, Verified, Dismissed, Escalated
    officer_notes = Column(Text, nullable=True)
    assigned_officer_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    due_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)
    
    project = relationship("Project", back_populates="alerts")
    decisions = relationship("Decision", back_populates="alert")

class Decision(Base):
    __tablename__ = "decisions"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"))
    officer_id = Column(String)
    classification = Column(String) # Confirmed, False alarm, Needs info, Escalate
    remarks = Column(Text)
    recommended_action = Column(Text, nullable=True)
    follow_up_date = Column(DateTime, nullable=True)
    feedback_tags = Column(String, nullable=True) # JSON or CSV
    decided_at = Column(DateTime, default=datetime.utcnow)
    
    alert = relationship("Alert", back_populates="decisions")

class AnomalyResult(Base):
    __tablename__ = "anomaly_results"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    update_id = Column(Integer, ForeignKey("project_history.id"))
    anomaly_score = Column(Float)
    flagged = Column(Boolean, default=False)
    reasons_json = Column(JSON, nullable=True)
    status = Column(String, default="Flagged") # Flagged, Accepted, Correction, Rejected
    created_at = Column(DateTime, default=datetime.utcnow)

class BenchmarkResult(Base):
    __tablename__ = "benchmark_results"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(String, ForeignKey("projects.id"))
    asof_date = Column(DateTime)
    peer_group_id = Column(String)
    progress_percentile = Column(Float)
    cost_growth_percentile = Column(Float)
    delay_percentile = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    action = Column(String)
    actor = Column(String, nullable=True)
    user_role = Column(String)
    object_type = Column(String, nullable=True)
    object_id = Column(String, nullable=True)
    details = Column(Text)
    before_ref = Column(Text, nullable=True)
    after_ref = Column(Text, nullable=True)
    session_ip = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)
