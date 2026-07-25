from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("", response_model=schemas.UserOut)
def create_user(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    user = models.User(display_name=payload.display_name.strip())
    db.add(user)
    db.commit()
    db.refresh(user)
    # default preference row
    pref = models.Preference(user_id=user.id)
    db.add(pref)
    db.commit()
    return user


@router.get("/{user_id}", response_model=schemas.UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}/preferences", response_model=schemas.PreferenceOut)
def update_preferences(user_id: int, payload: schemas.PreferenceIn, db: Session = Depends(get_db)):
    pref = db.query(models.Preference).filter(models.Preference.user_id == user_id).first()
    if not pref:
        raise HTTPException(status_code=404, detail="User not found")
    pref.style_goal = payload.style_goal
    pref.favorite_colors = payload.favorite_colors
    pref.preferred_occasion = payload.preferred_occasion
    db.commit()
    db.refresh(pref)
    return pref


@router.get("/{user_id}/preferences", response_model=schemas.PreferenceOut)
def get_preferences(user_id: int, db: Session = Depends(get_db)):
    pref = db.query(models.Preference).filter(models.Preference.user_id == user_id).first()
    if not pref:
        raise HTTPException(status_code=404, detail="Preferences not found")
    return pref
