from fastapi import APIRouter, Query

from ..mongo import tips_collection

router = APIRouter(prefix="/api/tips", tags=["tips"])

VALID_GOALS = {"structure", "balance", "elongate", "relaxed"}


@router.get("")
def get_tips(goal: str = Query(..., description="structure | balance | elongate | relaxed")):
    goal = goal.lower()
    if goal not in VALID_GOALS:
        goal = "balance"
    docs = list(tips_collection.find({"goal": goal}, {"_id": 0}))
    return docs
