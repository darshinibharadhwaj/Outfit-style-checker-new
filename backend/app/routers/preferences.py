from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..security import get_current_user

router = APIRouter(prefix="/api/preferences", tags=["preferences"])


def _get_or_create(db: Session, user: models.User) -> models.Preference:
    pref = db.query(models.Preference).filter(models.Preference.user_id == user.id).first()
    if pref is None:
        pref = models.Preference(user_id=user.id)
        db.add(pref)
        db.commit()
        db.refresh(pref)
    return pref


@router.get("", response_model=schemas.PreferenceOut)
def get_preferences(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return _get_or_create(db, user)


@router.put("", response_model=schemas.PreferenceOut)
def update_preferences(
    payload: schemas.PreferenceIn,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    pref = _get_or_create(db, user)
    pref.style_goal = payload.style_goal
    pref.favorite_colors = payload.favorite_colors
    pref.preferred_occasion = payload.preferred_occasion
    pref.skin_tone = payload.skin_tone
    db.commit()
    db.refresh(pref)
    return pref
