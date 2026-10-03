from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

StyleGoal = Literal["structure", "balance", "elongate", "relaxed"]
Occasion = Literal["casual", "office", "formal", "evening", "festival"]
SkinTone = Literal["fair", "wheatish", "medium", "dusky", "deep"]


# ---------- auth ----------
class RegisterIn(BaseModel):
    username: str = Field(min_length=3, max_length=30, pattern=r"^[A-Za-z0-9_]+$")
    password: str = Field(min_length=6, max_length=72)  # bcrypt only uses the first 72 bytes
    display_name: str = Field(min_length=1, max_length=100)


class LoginIn(BaseModel):
    username: str = Field(min_length=1, max_length=30)
    password: str = Field(min_length=1, max_length=72)


class UserOut(BaseModel):
    id: int
    username: str
    display_name: str

    class Config:
        from_attributes = True


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------- preferences ----------
class PreferenceIn(BaseModel):
    style_goal: StyleGoal
    favorite_colors: str = Field(default="", max_length=255)
    preferred_occasion: Occasion = "casual"
    skin_tone: SkinTone = "medium"


class PreferenceOut(PreferenceIn):
    class Config:
        from_attributes = True


# ---------- analyze ----------
Box = tuple[float, float, float, float]


class AnalyzeRequest(BaseModel):
    image_base64: str = Field(max_length=6_000_000)
    # fractional crop boxes (left, top, right, bottom), 0-1, chosen by the user
    top_box: Box
    bottom_box: Box

    @field_validator("top_box", "bottom_box")
    @classmethod
    def box_must_be_valid(cls, box: Box) -> Box:
        left, top, right, bottom = box
        if not (0 <= left < right <= 1 and 0 <= top < bottom <= 1):
            raise ValueError("box must be (left, top, right, bottom) with values between 0 and 1")
        return box


class AnalyzeResponse(BaseModel):
    check_id: int
    top_color: str
    bottom_color: str
    top_name: str
    bottom_name: str
    verdict: Literal["good", "ok", "change"]
    summary: str
    harmony_label: str
    harmony_score: float
    detail: str
    skin_advice: list[str]
    alternatives: list[str]
    accessories: list[str]
    footwear: list[str]
    tips: list[str]


class TipOut(BaseModel):
    goal: str
    title: str
    body: str


class HistoryItem(BaseModel):
    id: int
    top_color_hex: str
    bottom_color_hex: str
    harmony_label: str
    harmony_score: float
    created_at: datetime

    class Config:
        from_attributes = True
