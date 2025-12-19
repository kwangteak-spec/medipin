from pydantic import BaseModel, Field, EmailStr # 🚨 EmailStr 추가 임포트
from typing import List, Optional

# ... (기존 스키마 유지) ...

# 🚨 약품 상세 정보를 위한 출력 스키마 추가
class DrugDetailOut(BaseModel):
    item_seq: int = Field(..., alias="id")
    item_name: str
    company_name: str
    form_code_name: str
    # TODO: DB에 있는 다른 상세 정보 필드를 여기에 추가하세요.
    # main_effect: Optional[str] = None
    # ingredient: Optional[str] = None

    class Config:
        from_attributes = True
        populate_by_name = True

class UserMe(BaseModel):
    id: int
    email: EmailStr # 🚨 이제 오류 없이 사용 가능
    username: str
    role: str

    class Config:
        from_attributes = True 

class LoginRequest(BaseModel):
    email: EmailStr # 🚨 이제 오류 없이 사용 가능
    password: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str