from fastapi import APIRouter, Depends
from sqlalchemy import desc
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..security import get_current_user

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("", response_model=list[schemas.HistoryItem])
def get_history(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return (
        db.query(models.OutfitCheck)
        .filter(models.OutfitCheck.user_id == user.id)
        .order_by(desc(models.OutfitCheck.created_at))
        .limit(50)
        .all()
    )
