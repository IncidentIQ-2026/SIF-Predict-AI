from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from ..auth import current_user
from ..database import get_db
from ..models import Alert, AuthUser
from ..schemas import AlertRead, AlertUpdate

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/", response_model=list[AlertRead])
def list_alerts(db: Session = Depends(get_db), user: AuthUser = Depends(current_user)):
    return list(db.scalars(select(Alert).options(joinedload(Alert.report)).order_by(Alert.created_at.desc())).unique().all())


@router.patch("/{alert_id}", response_model=AlertRead)
def update_alert(alert_id: int, payload: AlertUpdate, db: Session = Depends(get_db)):
    alert = db.get(Alert, alert_id)
    if not alert:
        raise HTTPException(404, "Alert not found")
    alert.status = payload.status
    alert.acknowledged_by = payload.acknowledged_by
    db.commit()
    db.refresh(alert)
    return alert
