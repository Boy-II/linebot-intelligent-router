from sqlalchemy import create_engine, Column, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class User(Base):
    __tablename__ = 'line_users'

    line_id = Column(String, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSON)

# 資料庫連接設定
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@postgresql.zeabur.internal:5432/postgres')
engine = create_engine(DATABASE_URL)

# 創建資料表
Base.metadata.create_all(engine)

# 創建 Session 類別
SessionLocal = sessionmaker(bind=engine)

def get_db():
    """獲取資料庫會話"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection():
    """測試數據庫連接"""
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        print("✅ 資料庫連接成功")
        return True
    except Exception as e:
        print(f"❌ 資料庫連接失敗: {e}")
        return False 