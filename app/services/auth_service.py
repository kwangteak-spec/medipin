# app/services/auth_service.py

from passlib.context import CryptContext
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, datetime, timedelta
import traceback

from fastapi import HTTPException

from app.models.user import UserProfile
from app.models.refresh_token import RefreshToken
from app.security.jwt_handler import create_access_token, create_refresh_token
from app.schemas.user import FamilyMemberRequest  # 가족 구성원 요청 스키마 임포트

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# =======================================================
# 0. 비밀번호 해싱 및 검증
# =======================================================
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# =======================================================
# 0-1. Refresh Token DB 저장
# =======================================================
def issue_refresh_token(db: Session, user_id: int, token: str, days: int = 7) -> RefreshToken:
    """
    refresh_tokens 테이블에 refresh token을 저장합니다.
    DB 스키마 상 expires_at (NOT NULL)을 반드시 채워야 합니다.
    """
    rt = RefreshToken(
        user_id=user_id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(days=days),
        revoked=False,
    )
    db.add(rt)
    db.commit()
    db.refresh(rt)
    return rt


# =======================================================
# 1. 회원가입 (Register User)
# =======================================================
def register_user(
    db: Session,
    email: str,
    password: str,
    name: str,
    phone_num: str,
    age: int,
    birth_date: Optional[date] = None,
    gender: Optional[str] = None,
    height: Optional[float] = None,
    weight: Optional[float] = None,
    special_note: Optional[str] = None,
):
    # 이메일 중복 체크
    if db.query(UserProfile).filter(UserProfile.email == email).first():
        raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다.")

    hashed_pw = hash_password(password)

    user_profile = UserProfile(
        email=email,
        hashed_password=hashed_pw,
        phone_num=phone_num,
        name=name,
        age=age,
        birth_date=birth_date,
        gender=gender,
        height=height,
        weight=weight,
        special_note=special_note,
        user_id=None,  # 주 사용자 생성 후 id로 맞춤
    )

    try:
        db.add(user_profile)
        db.commit()
        db.refresh(user_profile)

        # user_id를 자기 자신 id로 세팅(주 사용자 식별용)
        if user_profile.user_id is None:
            user_profile.user_id = user_profile.id
            db.commit()
            db.refresh(user_profile)

        print("✅ 등록된 유저 정보:", user_profile.__dict__)
        return user_profile

    except Exception as e:
        db.rollback()
        print("❌ 회원가입 중 에러:", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"DB 저장 실패: {str(e)}")


# =======================================================
# 2. 로그인 (Login User)
# =======================================================
def login_user(db: Session, email: str, password: str):
    user = db.query(UserProfile).filter(UserProfile.email == email).first()

    # 인증 실패는 401로 명확히 처리
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다.")

    access_token = create_access_token({"sub": user.email})
    refresh_token = create_refresh_token({"sub": user.email})

    # refresh token DB 저장
    try:
        issue_refresh_token(db, user_id=user.id, token=refresh_token, days=7)
    except Exception as e:
        db.rollback()
        print("❌ 리프레시 토큰 저장 실패:", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"리프레시 토큰 저장 실패: {str(e)}")

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


# =======================================================
# 3. 가족 구성원 추가 (Add Family Member)
# =======================================================
def add_family_member(db: Session, owner_id: int, member_data: FamilyMemberRequest):
    """
    ⚠ 현재 user_profile 테이블은 email, hashed_password가 NOT NULL입니다.
    따라서 가족 구성원을 같은 테이블에 저장하려면 더미 값이라도 채워야 INSERT가 가능합니다.
    (권장: 가족 구성원 전용 테이블로 분리)

    여기서는 '작동 우선'을 위해 더미 email/hashed_password를 넣는 임시 방식을 사용합니다.
    """
    dummy_email = f"family_{owner_id}_{int(datetime.utcnow().timestamp())}@local"
    dummy_password = hash_password("TEMP_FAMILY_MEMBER_PASSWORD")

    new_member = UserProfile(
        user_id=owner_id,
        name=member_data.name,
        age=member_data.age,

        # 임시 더미 인증 정보(INSERT 가능하게)
        email=dummy_email,
        hashed_password=dummy_password,
        phone_num=None,
    )

    try:
        db.add(new_member)
        db.commit()
        db.refresh(new_member)
        return new_member
    except Exception as e:
        db.rollback()
        print("❌ 가족 구성원 추가 실패:", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"가족 구성원 저장 실패: {str(e)}")
