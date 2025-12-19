# app/models/refresh_token.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db import Base

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_profile.id", ondelete="CASCADE"), nullable=False, index=True)

    token = Column(String(512), nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, nullable=False, server_default=text("0"))

    created_at = Column(DateTime, server_default=func.now(), nullable=True)

    user = relationship("UserProfile", back_populates="refresh_tokens")
