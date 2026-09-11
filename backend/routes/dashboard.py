from fastapi import APIRouter, Depends
from sqlalchemy import case, desc, func, select
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Report

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def rows(db, field):
    stmt = select(field.label("name"), func.count(Report.id).label("reports"), func.sum(case((Report.sif_label == "SIF-Potential", 1), else_=0)).label("sif_reports")).group_by(field).order_by(desc("sif_reports"))
    return [{"name": row.name, "reports": row.reports, "sif_reports": row.sif_reports or 0, "density": round((row.sif_reports or 0) / row.reports * 100, 1)} for row in db.execute(stmt).all()]


@router.get("/stats")
def stats(db: Session = Depends(get_db)):
    total = db.scalar(select(func.count(Report.id))) or 0
    sif = db.scalar(select(func.count(Report.id)).where(Report.sif_label == "SIF-Potential")) or 0
    high = db.scalar(select(func.count(Report.id)).where(Report.risk_level == "HIGH")) or 0
    return {"total_reports": total, "sif_reports": sif, "non_sif_reports": total - sif, "high_risk_alerts": high, "sif_percentage": round(sif / total * 100, 1) if total else 0}


@router.get("/sif-trend")
def sif_trend(db: Session = Depends(get_db)):
    day = func.date(Report.created_at)
    stmt = select(day.label("date"), func.count(Report.id).label("reports"), func.sum(case((Report.sif_label == "SIF-Potential", 1), else_=0)).label("sif_reports")).group_by(day).order_by(day)
    return [{"date": str(row.date), "reports": row.reports, "sif_reports": row.sif_reports or 0} for row in db.execute(stmt).all()]


@router.get("/top-sites")
def top_sites(db: Session = Depends(get_db)): return rows(db, Report.location)

@router.get("/top-activities")
def top_activities(db: Session = Depends(get_db)): return rows(db, Report.activity)

@router.get("/top-rules")
def top_rules(db: Session = Depends(get_db)): return rows(db, Report.life_saving_rule)


@router.get("/precursors")
def precursors(db: Session = Depends(get_db)):
    return {"barriers": rows(db, Report.barrier_failure), "rules": rows(db, Report.life_saving_rule), "activities": rows(db, Report.activity)}
