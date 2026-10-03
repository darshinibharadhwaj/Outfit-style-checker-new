from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)  # bcrypt hash, never the real password
    display_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    preference = relationship("Preference", back_populates="user", uselist=False)
    checks = relationship("OutfitCheck", back_populates="user")


class Preference(Base):
    """
    User-chosen style preferences. Note: goal, occasion and skin tone are all
    self-selected from a menu -- never inferred from a photo or body analysis.
    """

    __tablename__ = "preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    style_goal = Column(String(50), default="balance")
    favorite_colors = Column(String(255), default="")
    preferred_occasion = Column(String(50), default="casual")
    skin_tone = Column(String(20), default="medium")

    user = relationship("User", back_populates="preference")


class OutfitCheck(Base):
    """Summary record of one on-demand outfit color check."""

    __tablename__ = "outfit_checks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    top_color_hex = Column(String(7))
    bottom_color_hex = Column(String(7))
    harmony_label = Column(String(50))
    harmony_score = Column(Float)
    mongo_log_id = Column(String(50))  # links to full detail doc in MongoDB
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="checks")
