from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator
from dotenv import load_dotenv
import os

# 현재 파일 위치 기준으로 최상위 루트의 .env 경로 계산
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(BASE_DIR, ".env")

load_dotenv(env_path)

class Settings(BaseSettings):
    APP_NAME: str = "Medipin"
    MYSQL_USER: str = "user1"  # 프로젝트 설정에 맞춰 user1으로 변경
    MYSQL_PASSWORD: str = "123"  # 여기에비밀번호작성 (123으로 설정됨)
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: str = "3306"
    MYSQL_DB: str = "medipin"
    REDIS_URL: str = "redis://localhost:6379"
    
    # DATABASE_URL은 초기화 시 다른 필드들을 기반으로 자동 구성됩니다.
    DATABASE_URL: str = ""

    @model_validator(mode='after')
    def assemble_db_url(self) -> 'Settings':
        # MYSQL_USER, PASSWORD 등을 조합하여 자동으로 DATABASE_URL 생성
        self.DATABASE_URL = f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"
        return self
    
    # 🚨 GEMINI_API_KEY
    GEMINI_API_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=env_path,
        env_file_encoding='utf-8',
        extra="ignore"
    )

settings = Settings()