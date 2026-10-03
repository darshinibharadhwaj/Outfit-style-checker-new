from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_dummy,
    verify_password,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=schemas.TokenOut, status_code=201)
def register(payload: schemas.RegisterIn, db: Session = Depends(get_db)):
    username = payload.username.lower()
    if db.query(models.User).filter(models.User.username == username).first():
        raise HTTPException(status_code=409, detail="That username is already taken.")

    user = models.User(
        username=username,
        display_name=payload.display_name.strip(),
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:  # two people registered the same name at the same moment
        db.rollback()
        raise HTTPException(status_code=409, detail="That username is already taken.")
    db.refresh(user)

    db.add(models.Preference(user_id=user.id))  # default preferences
    db.commit()

    return schemas.TokenOut(access_token=create_access_token(user.id), user=user)


@router.post("/login", response_model=schemas.TokenOut)
def login(payload: schemas.LoginIn, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == payload.username.lower()).first()
    if user is None:
        verify_dummy(payload.password)  # keep timing similar for unknown usernames
        raise HTTPException(status_code=401, detail="Incorrect username or password.")
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect username or password.")
    return schemas.TokenOut(access_token=create_access_token(user.id), user=user)


@router.get("/me", response_model=schemas.UserOut)
def me(current_user: models.User = Depends(get_current_user)):
    return current_user
