from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings  
import pymysql


DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_conn():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="mysqlbig",
        database="medipin",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )