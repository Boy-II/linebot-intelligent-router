from sqlalchemy import create_engine, Column, String, DateTime, JSON, Integer
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
    user_metadata = Column(JSON)  # 改名避免保留字衝突

class UserContext(Base):
    __tablename__ = 'user_contexts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False)
    context_name = Column(String(100), nullable=False)
    parameters = Column(JSON)
    lifespan = Column(Integer, default=5)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserTask(Base):
    __tablename__ = 'user_tasks'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False)
    task_type = Column(String(100), nullable=False)
    task_data = Column(JSON)
    status = Column(String(50), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

# 資料庫連接設定
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@postgresql.zeabur.internal:5432/postgres')
print(f"連接資料庫: {DATABASE_URL.replace(':', ':*****@', 1) if '@' in DATABASE_URL else DATABASE_URL}")

engine = create_engine(DATABASE_URL)

# 創建資料表
try:
    print("正在創建資料表...")
    Base.metadata.create_all(engine)
    print("✅ 資料表創建成功")
    
    # 檢查表是否存在
    with engine.connect() as conn:
        result = conn.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND (table_name LIKE 'line_%' OR table_name LIKE 'user_%')
            ORDER BY table_name
        """)
        tables = [row[0] for row in result]
        print(f"✅ 發現 LineBot 相關表: {tables}")
except Exception as e:
    print(f"❌ 創建資料表失敗: {e}")

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