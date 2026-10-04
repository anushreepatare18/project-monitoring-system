from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./backend/pragya.db")
# Fix postgres:// to postgresql:// for SQLAlchemy if provided by some providers (like Heroku)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Project(Base):
    __tablename__ = "projects"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    sector = Column(String, index=True)
    ministry = Column(String, index=True)
    implementing_agency = Column(String)
    
    # Financials
    original_cost_cr = Column(Float, default=0.0)
    expenditure_cr = Column(Float, default=0.0)
    cost_overrun_pct = Column(Float, default=0.0)
    
    # Schedule
    delay_months = Column(Float, default=0.0)
    physical_progress_pct = Column(Float, default=0.0)
    status = Column(String, default="Ongoing")
    
    # Risk
    risk_score = Column(Float, default=0.0)
    risk_level = Column(String, default="Low")
    is_anomalous = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(String, ForeignKey("projects.id"))
    risk_score = Column(Float)
    message = Column(Text)
    status = Column(String, default="Open") # Open, Verified, Dismissed
    officer_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    action = Column(String)
    user_role = Column(String)
    details = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

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

class SectorThreshold(Base):
    __tablename__ = "sector_thresholds"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sector = Column(String, unique=True, index=True)
    critical_threshold = Column(Float, default=75.0)
    high_threshold = Column(Float, default=50.0)

class ModelVersion(Base):
    __tablename__ = "model_versions"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    version = Column(String, index=True)
    deployed_at = Column(DateTime, default=datetime.utcnow)
    accuracy = Column(Float, nullable=True)
    pr_auc = Column(Float, nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=False)

Base.metadata.create_all(bind=engine)
