from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import AnalysisRequest, AnalysisResult
from ..routes.reports import save_report
from ..services.nlp_engine import predict

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/", response_model=AnalysisResult)
def analyze(payload: AnalysisRequest, db: Session = Depends(get_db)):
    result = predict(payload.report_text, payload.activity)
    if payload.persist:
        report = save_report(payload, db)
        result["report_id"] = report.id
    return result
