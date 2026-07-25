from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("/{user_id}", response_model=list[schemas.HistoryItem])
def get_history(user_id: int, db: Session = Depends(get_db)):
    checks = (
        db.query(models.OutfitCheck)
        .filter(models.OutfitCheck.user_id == user_id)
        .order_by(desc(models.OutfitCheck.created_at))
        .limit(50)
        .all()
    )
    return checks
