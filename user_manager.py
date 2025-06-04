import logging
from datetime import datetime
from typing import Dict, Optional, List
from sqlalchemy.orm import Session
from models import User, get_db
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager

class UserManager:
    """
    用戶管理系統 - PostgreSQL 版本
    """
    
    def __init__(self):
        """
        初始化用戶管理器
        """
        self._setup_logging()
    
    def _setup_logging(self):
        """設置日誌系統"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('UserManager')
    
    @contextmanager
    def _get_db(self):
        """獲取資料庫會話的上下文管理器"""
        db = next(get_db())
        try:
            yield db
        finally:
            db.close()

    def add_user(self, line_id: str, name: str, email: str, **kwargs) -> bool:
        """新增用戶"""
        try:
            with self._get_db() as db:
                user = User(
                    line_id=line_id,
                    name=name,
                    email=email,
                    metadata=kwargs
                )
                db.add(user)
                db.commit()
                self.logger.info(f"已新增用戶: {line_id}")
                return True
        except SQLAlchemyError as e:
            self.logger.error(f"新增用戶失敗: {e}")
            return False

    def get_user_by_line_id(self, line_id: str) -> Optional[Dict]:
        """根據 LINE ID 獲取用戶"""
        try:
            with self._get_db() as db:
                user = db.query(User).filter(User.line_id == line_id).first()
                if user:
                    return {
                        'line_id': user.line_id,
                        'name': user.name,
                        'email': user.email,
                        **user.metadata
                    }
                return None
        except SQLAlchemyError as e:
            self.logger.error(f"獲取用戶失敗: {e}")
            return None

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """根據 email 獲取用戶"""
        try:
            with self._get_db() as db:
                user = db.query(User).filter(User.email == email).first()
                if user:
                    return {
                        'line_id': user.line_id,
                        'name': user.name,
                        'email': user.email,
                        **user.metadata
                    }
                return None
        except SQLAlchemyError as e:
            self.logger.error(f"獲取用戶失敗: {e}")
            return None

    def get_user_by_name(self, name: str) -> Optional[Dict]:
        """根據名稱獲取用戶"""
        try:
            with self._get_db() as db:
                user = db.query(User).filter(User.name == name).first()
                if user:
                    return {
                        'line_id': user.line_id,
                        'name': user.name,
                        'email': user.email,
                        **user.metadata
                    }
                return None
        except SQLAlchemyError as e:
            self.logger.error(f"獲取用戶失敗: {e}")
            return None

    def update_user(self, line_id: str, **kwargs) -> bool:
        """更新用戶資料"""
        try:
            with self._get_db() as db:
                user = db.query(User).filter(User.line_id == line_id).first()
                if not user:
                    return False

                # 更新基本欄位
                if 'name' in kwargs:
                    user.name = kwargs.pop('name')
                if 'email' in kwargs:
                    user.email = kwargs.pop('email')

                # 更新其他元數據
                if user.metadata is None:
                    user.metadata = {}
                user.metadata.update(kwargs)
                
                db.commit()
                self.logger.info(f"已更新用戶: {line_id}")
                return True
        except SQLAlchemyError as e:
            self.logger.error(f"更新用戶失敗: {e}")
            return False

    def delete_user(self, line_id: str) -> bool:
        """刪除用戶"""
        try:
            with self._get_db() as db:
                user = db.query(User).filter(User.line_id == line_id).first()
                if user:
                    db.delete(user)
                    db.commit()
                    self.logger.info(f"已刪除用戶: {line_id}")
                    return True
                return False
        except SQLAlchemyError as e:
            self.logger.error(f"刪除用戶失敗: {e}")
            return False

    def search_users(self, query: str) -> List[Dict]:
        """搜尋用戶"""
        try:
            with self._get_db() as db:
                users = db.query(User).filter(
                    (User.name.ilike(f"%{query}%")) |
                    (User.email.ilike(f"%{query}%"))
                ).all()
                
                return [{
                    'line_id': user.line_id,
                    'name': user.name,
                    'email': user.email,
                    **user.metadata
                } for user in users]
        except SQLAlchemyError as e:
            self.logger.error(f"搜尋用戶失敗: {e}")
            return []

    def get_user_display_name(self, line_id: str) -> str:
        """獲取用戶顯示名稱"""
        user = self.get_user_by_line_id(line_id)
        return user['name'] if user else line_id

    def get_user_email(self, line_id: str) -> Optional[str]:
        """獲取用戶 email"""
        user = self.get_user_by_line_id(line_id)
        return user['email'] if user else None

    def is_registered_user(self, line_id: str) -> bool:
        """檢查用戶是否已註冊"""
        return self.get_user_by_line_id(line_id) is not None

    def get_all_users(self) -> List[Dict]:
        """獲取所有用戶"""
        try:
            with self._get_db() as db:
                users = db.query(User).all()
                return [{
                    'line_id': user.line_id,
                    'name': user.name,
                    'email': user.email,
                    **user.metadata
                } for user in users]
        except SQLAlchemyError as e:
            self.logger.error(f"獲取所有用戶失敗: {e}")
            return []

    def get_statistics(self) -> Dict:
        """獲取統計資訊"""
        try:
            with self._get_db() as db:
                total_users = db.query(User).count()
                latest_user = db.query(User).order_by(User.created_at.desc()).first()
                
                return {
                    "total_users": total_users,
                    "latest_user_created": latest_user.created_at.isoformat() if latest_user else None,
                    "database_type": "PostgreSQL",
                    "version": "1.0"
                }
        except SQLAlchemyError as e:
            self.logger.error(f"獲取統計資訊失敗: {e}")
            return {
                "total_users": 0,
                "latest_user_created": None,
                "database_type": "PostgreSQL",
                "version": "1.0",
                "error": str(e)
            }

    def get_health_status(self) -> Dict:
        """獲取健康狀態"""
        try:
            with self._get_db() as db:
                db.query(User).first()
                return {
                    "status": "healthy",
                    "database": "connected",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
