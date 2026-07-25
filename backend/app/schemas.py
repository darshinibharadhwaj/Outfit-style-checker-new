from pydantic import BaseModel
from datetime import datetime


class UserCreate(BaseModel):
    display_name: str


class UserOut(BaseModel):
    id: int
    display_name: str

    class Config:
        from_attributes = True


class PreferenceIn(BaseModel):
    style_goal: str  # 'structure' | 'balance' | 'elongate' | 'relaxed'
    favorite_colors: str = ""
    preferred_occasion: str = "casual"


class PreferenceOut(PreferenceIn):
    class Config:
        from_attributes = True


class AnalyzeRequest(BaseModel):
    user_id: int
    image_base64: str
    # fractional crop boxes (left, top, right, bottom), 0-1, chosen by the user
    top_box: tuple[float, float, float, float]
    bottom_box: tuple[float, float, float, float]


class ColorOut(BaseModel):
    hex: str


class AnalyzeResponse(BaseModel):
    check_id: int
    top_color: str
    bottom_color: str
    harmony_label: str
    harmony_score: float
    detail: str
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
