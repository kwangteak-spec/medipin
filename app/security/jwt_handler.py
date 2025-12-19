# app/security/jwt_handler.py 파일 전체 내용

from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db import get_db # 🚨 DB 접근을 위해 필요
from app.models.user import UserProfile # 🚨 사용자 조회를 위해 필요

# 🚨 반드시 정의해야 하는 변수 (오류의 주요 원인)
SECRET_KEY = "your-very-long-and-secure-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7


# 🚨 JWT 토큰을 헤더에서 추출하기 위한 객체
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login") 


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS) 
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# 🚨 누락되어 오류를 일으킨 함수
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> int:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 정보를 확인할 수 없습니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 1. 토큰 복호화 및 검증
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # 2. 토큰에서 사용자 식별 정보(subject) 추출
        user_email: str = payload.get("sub")
        
        if user_email is None:
            raise credentials_exception
            
        # 3. DB에서 이메일을 통해 주사용자 ID(PK)를 조회
        # 🚨 DB 칼럼 e_mail 사용
        user = db.query(UserProfile).filter(UserProfile.email == user_email).first()
        
        if user is None:
             raise credentials_exception
        
        # 4. 주사용자의 PK (id) 반환
        return user.id 

    except JWTError:
        raise credentials_exception