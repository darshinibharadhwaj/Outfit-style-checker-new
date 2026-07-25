import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..color_utils import decode_base64_image, analyze_region, score_harmony
from ..mongo import analysis_logs_collection, tips_collection

router = APIRouter(prefix="/api/analyze", tags=["analyze"])


@router.post("", response_model=schemas.AnalyzeResponse)
def analyze_outfit(payload: schemas.AnalyzeRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        image = decode_base64_image(payload.image_base64)
    except Exception:
        raise HTTPException(status_code=400, detail="Could not decode image")

    top = analyze_region(image, payload.top_box)
    bottom = analyze_region(image, payload.bottom_box)
    harmony = score_harmony(top, bottom)

    # Pull a couple of relevant tips based on the user's own chosen style goal
    pref = db.query(models.Preference).filter(models.Preference.user_id == user.id).first()
    goal = pref.style_goal if pref else "balance"
    tip_docs = list(tips_collection.find({"goal": goal}, {"_id": 0}).limit(2))
    tips = [f'{t["title"]}: {t["body"]}' for t in tip_docs]

    # Full detail log goes to MongoDB (flexible schema)
    mongo_log_id = str(uuid.uuid4())
    analysis_logs_collection.insert_one({
        "log_id": mongo_log_id,
        "user_id": user.id,
        "top_rgb": top.rgb,
        "bottom_rgb": bottom.rgb,
        "top_hex": top.hex,
        "bottom_hex": bottom.hex,
        "harmony": harmony,
        "style_goal": goal,
        "created_at": datetime.utcnow().isoformat(),
    })

    # Summary row goes to MySQL (structured, queryable history)
    check = models.OutfitCheck(
        user_id=user.id,
        top_color_hex=top.hex,
        bottom_color_hex=bottom.hex,
        harmony_label=harmony["label"],
        harmony_score=harmony["score"],
        mongo_log_id=mongo_log_id,
    )
    db.add(check)
    db.commit()
    db.refresh(check)

    return schemas.AnalyzeResponse(
        check_id=check.id,
        top_color=top.hex,
        bottom_color=bottom.hex,
        harmony_label=harmony["label"],
        harmony_score=harmony["score"],
        detail=harmony["detail"],
        tips=tips,
    )
