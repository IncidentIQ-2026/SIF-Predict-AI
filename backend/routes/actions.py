from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import CorrectiveAction
from ..schemas import ActionCreate, ActionRead, ActionUpdate

router = APIRouter(prefix="/actions", tags=["actions"])


@router.post("/", response_model=ActionRead, status_code=201)
def create_action(payload: ActionCreate, db: Session = Depends(get_db)):
    action = CorrectiveAction(**payload.model_dump())
    db.add(action)
    db.commit()
    db.refresh(action)
    return action


@router.get("/", response_model=list[ActionRead])
def list_actions(db: Session = Depends(get_db)):
    return list(db.scalars(select(CorrectiveAction).order_by(CorrectiveAction.due_date)).all())


@router.patch("/{action_id}", response_model=ActionRead)
def update_action(action_id: int, payload: ActionUpdate, db: Session = Depends(get_db)):
    action = db.get(CorrectiveAction, action_id)
    if not action:
        raise HTTPException(404, "Action not found")
    action.status = payload.status
    action.completed_at = datetime.utcnow() if payload.status == "Completed" else None
    db.commit()
    db.refresh(action)
    return action
