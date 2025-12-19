# app/security/password_handler.py (신규 파일)

from passlib.context import CryptContext

# CryptContext 설정: bcrypt는 비밀번호 해시 표준 방식
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """ 평문 비밀번호와 해시된 비밀번호를 비교합니다. """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """ 평문 비밀번호를 해시하여 반환합니다. """
    return pwd_context.hash(password)