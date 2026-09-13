from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from ..auth import current_user
from ..database import get_db
from ..models import AIAnalysis, Alert, AuthUser, Report
from ..schemas import AnalysisRequest, AnalysisResult, ReportCreate, ReportRead, StatusUpdate
from ..services.nlp_engine import predict
from ..services.email_service import send_hazard_email

router = APIRouter(prefix="/reports", tags=["reports"])


def save_report(payload: ReportCreate, db: Session, user: AuthUser | None = None) -> Report:
    result = predict(payload.report_text, payload.activity)
    report_fields = {key: getattr(payload, key) for key in ("report_text", "report_type", "location", "department")}
    report = Report(**report_fields, **{key: value for key, value in result.items() if key != "explanation"})
    db.add(report)
    db.flush()
    db.add(AIAnalysis(report_id=report.id, explanation=result["explanation"]))
    if result["risk_level"] == "HIGH":
        db.add(Alert(report_id=report.id, severity="HIGH"))
        recipients = [user.email] if user else []
        recipients.extend(email.strip() for email in __import__("os").getenv("HSE_ALERT_EMAILS", "").split(","))
        send_hazard_email(recipients, payload.location, result["life_saving_rule"], payload.report_text, result["sif_probability"])
    db.commit()
    db.refresh(report)
    return report


@router.post("/", response_model=ReportRead, status_code=201)
def create_report(payload: ReportCreate, db: Session = Depends(get_db), user: AuthUser = Depends(current_user)):
    return save_report(payload, db, user)


@router.get("/", response_model=list[ReportRead])
def list_reports(search: str | None = None, status: str | None = None, risk: str | None = None, limit: int = Query(50, ge=1, le=200), db: Session = Depends(get_db), user: AuthUser = Depends(current_user)):
    query = select(Report).order_by(Report.created_at.desc()).limit(limit)
    if search:
        query = query.where(or_(Report.report_text.ilike(f"%{search}%"), Report.location.ilike(f"%{search}%"), Report.activity.ilike(f"%{search}%")))
    if status:
        query = query.where(Report.status == status)
    if risk:
        query = query.where(Report.risk_level == risk.upper())
    return list(db.scalars(query).all())


@router.get("/{report_id}", response_model=ReportRead)
def get_report(report_id: int, db: Session = Depends(get_db), user: AuthUser = Depends(current_user)):
    report = db.get(Report, report_id)
    if not report:
        raise HTTPException(404, "Report not found")
    return report


@router.patch("/{report_id}/status", response_model=ReportRead)
def update_report_status(report_id: int, payload: StatusUpdate, db: Session = Depends(get_db), user: AuthUser = Depends(current_user)):
    report = db.get(Report, report_id)
    if not report:
        raise HTTPException(404, "Report not found")
    report.status = payload.status
    db.commit()
    db.refresh(report)
    return report
