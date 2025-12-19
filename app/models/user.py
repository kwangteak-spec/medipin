# app/models/user.py

from sqlalchemy import Column, Integer, String, Float, Date, Text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db import Base

class UserProfile(Base):
    __tablename__ = "user_profile"

    id = Column(Integer, primary_key=True, index=True)

    # ✅ 방금 DB에 추가한 컬럼 (주사용자 그룹핑용)
    user_id = Column(Integer, ForeignKey("user_profile.id"), nullable=True, index=True)

    email = Column(String(200), unique=True, nullable=False)
    pw = Column(String(255), nullable=True)              # DB에 있으니 유지(안 써도 됨)
    hashed_password = Column(String(255), nullable=False)

    phone_num = Column(String(20), nullable=True)
    user_profile_photo = Column(Text, nullable=True)
    name = Column(String(100), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=True)

    age = Column(Integer, nullable=True)
    birth_date = Column(Date, nullable=True)
    gender = Column(String(10), nullable=True)
    height = Column(Float, nullable=True)
    weight = Column(Float, nullable=True)
    special_note = Column(String(500), nullable=True)

    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # ✅ 가족 구성원 (PatientProfile) 관계 설정
    patient_profiles = relationship(
        "PatientProfile",
        back_populates="user",
        cascade="all, delete-orphan",
    )

class PatientProfile(Base):
    __tablename__ = "patient_profile"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_profile.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=True)
    relation = Column(String(50), nullable=True)
    birth_date = Column(Date, nullable=True)
    gender = Column(String(10), nullable=True)
    special_note = Column(String(500), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=True)

    # User와의 관계
    user = relationship("UserProfile", back_populates="patient_profiles")
    
    # ActiveMedication과의 관계 (1:N)
    active_medications = relationship("ActiveMedication", back_populates="patient", cascade="all, delete-orphan")
