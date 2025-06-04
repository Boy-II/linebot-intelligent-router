import json
import os
from datetime import datetime
from models import User, SessionLocal
from sqlalchemy.exc import SQLAlchemyError
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_json_data(json_file_path):
    """載入 JSON 資料"""
    try:
        if not os.path.exists(json_file_path):
            logger.error(f"找不到 JSON 檔案：{json_file_path}")
            return None
        
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        logger.error(f"載入 JSON 資料失敗：{e}")
        return None

def migrate_users():
    """將用戶資料從 JSON 遷移到 PostgreSQL"""
    json_file_path = "data/users/users.json"
    data = load_json_data(json_file_path)
    
    if not data or "users" not in data:
        logger.error("無效的用戶資料格式")
        return False
    
    db = SessionLocal()
    try:
        for line_id, user_data in data["users"].items():
            # 準備基本資料
            user = User(
                line_id=line_id,
                name=user_data.get("name"),
                email=user_data.get("email")
            )
            
            # 準備元數據
            metadata = {k: v for k, v in user_data.items() 
                      if k not in ["line_id", "name", "email"]}
            user.metadata = metadata
            
            # 設置時間戳
            if "created_at" in user_data:
                try:
                    user.created_at = datetime.fromisoformat(user_data["created_at"])
                except ValueError:
                    user.created_at = datetime.utcnow()
            
            # 新增到資料庫
            db.add(user)
            logger.info(f"遷移用戶資料：{line_id}")
        
        # 提交所有變更
        db.commit()
        logger.info("資料遷移完成")
        return True
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"資料遷移失敗：{e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    migrate_users() 