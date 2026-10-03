import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..advice import build_advice
from ..color_utils import analyze_region, decode_base64_image, score_harmony
from ..database import get_db
from ..mongo import analysis_logs_collection, tips_collection
from ..security import get_current_user

router = APIRouter(prefix="/api/analyze", tags=["analyze"])


@router.post("", response_model=schemas.AnalyzeResponse)
def analyze_outfit(
    payload: schemas.AnalyzeRequest,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    try:
        image = decode_base64_image(payload.image_base64)
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read the image. Please try again.")

    try:
        top = analyze_region(image, payload.top_box)
        bottom = analyze_region(image, payload.bottom_box)
    except ValueError:
        raise HTTPException(status_code=400, detail="Could not read colours from the photo.")
    harmony = score_harmony(top, bottom)

    # Everything below uses choices the user made themselves
    pref = db.query(models.Preference).filter(models.Preference.user_id == user.id).first()
    goal = pref.style_goal if pref else "balance"
    occasion = pref.preferred_occasion if pref else "casual"
    skin_tone = pref.skin_tone if pref else "medium"

    advice = build_advice(top, bottom, harmony, skin_tone, occasion)

    tip_docs = list(tips_collection.find({"goal": goal}, {"_id": 0}).limit(2))
    tips = [f'{t["title"]}: {t["body"]}' for t in tip_docs]

    # Full detail log goes to MongoDB (flexible schema). The photo itself is NOT saved.
    mongo_log_id = str(uuid.uuid4())
    analysis_logs_collection.insert_one({
        "log_id": mongo_log_id,
        "user_id": user.id,
        "top_rgb": top.rgb,
        "bottom_rgb": bottom.rgb,
        "top_hex": top.hex,
        "bottom_hex": bottom.hex,
        "top_name": advice["top_name"],
        "bottom_name": advice["bottom_name"],
        "harmony": harmony,
        "style_goal": goal,
        "occasion": occasion,
        "skin_tone": skin_tone,
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
        **advice,
    )
