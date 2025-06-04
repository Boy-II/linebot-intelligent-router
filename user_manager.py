import json
import os
import shutil
from datetime import datetime
from typing import Dict, Optional, List
import logging

class UserManager:
    """
    用戶管理系統 - Docker持久化版本
    支援數據持久化、自動備份和容器重啟後數據恢復
    """
    
    def __init__(self, data_dir="/app/data", backup_interval_hours=24):
        """
        初始化用戶管理器
        
        Args:
            data_dir: 數據目錄路徑 (Docker volume mount point)
            backup_interval_hours: 自動備份間隔（小時）
        """
        self.data_dir = data_dir
        self.users_dir = os.path.join(data_dir, "users")
        self.backups_dir = os.path.join(data_dir, "backups")
        self.logs_dir = os.path.join(data_dir, "logs")
        
        self.users_file_path = os.path.join(self.users_dir, "users.json")
        self.backup_interval_hours = backup_interval_hours
        
        # 確保目錄存在
        self._ensure_directories()
        
        # 設置日誌
        self._setup_logging()
        
        # 載入用戶資料
        self.users_data = self._load_users()
        
        # 檢查是否需要備份
        self._check_and_backup()
    
    def _ensure_directories(self):
        """確保所有必要的目錄存在"""
        directories = [self.data_dir, self.users_dir, self.backups_dir, self.logs_dir]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            print(f"確保目錄存在: {directory}")
    
    def _setup_logging(self):
        """設置日誌系統"""
        log_file = os.path.join(self.logs_dir, f"user_manager_{datetime.now().strftime('%Y%m%d')}.log")
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger('UserManager')
        self.logger.info(f"用戶管理器日誌初始化完成: {log_file}")
    
    def _load_users(self) -> Dict:
        """載入用戶資料，支援從備份恢復"""
        try:
            if os.path.exists(self.users_file_path):
                with open(self.users_file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.logger.info(f"已載入 {len(data.get('users', {}))} 個用戶資料")
                
                # 驗證數據完整性
                if self._validate_data_integrity(data):
                    return data
                else:
                    self.logger.warning("數據完整性檢查失敗，嘗試從備份恢復")
                    return self._restore_from_backup() or self._create_default_structure()
            else:
                self.logger.info("用戶資料檔案不存在，創建新檔案")
                return self._create_default_structure()
                
        except Exception as e:
            self.logger.error(f"載入用戶資料失敗: {e}")
            # 嘗試從最新備份恢復
            restored_data = self._restore_from_backup()
            if restored_data:
                return restored_data
            else:
                return self._create_default_structure()
    
    def _validate_data_integrity(self, data: Dict) -> bool:
        """驗證數據完整性"""
        try:
            required_keys = ['metadata', 'users', 'email_index', 'name_index']
            
            for key in required_keys:
                if key not in data:
                    self.logger.error(f"缺少必要鍵值: {key}")
                    return False
            
            # 檢查用戶數據和索引的一致性
            users = data['users']
            email_index = data['email_index']
            name_index = data['name_index']
            
            for line_id, user_info in users.items():
                email = user_info.get('email')
                name = user_info.get('name')
                
                if email and email_index.get(email) != line_id:
                    self.logger.warning(f"Email索引不一致: {email}")
                    return False
                
                if name and name_index.get(name) != line_id:
                    self.logger.warning(f"姓名索引不一致: {name}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"數據完整性檢查失敗: {e}")
            return False
    
    def _restore_from_backup(self) -> Optional[Dict]:
        """從最新的備份恢復數據"""
        try:
            if not os.path.exists(self.backups_dir):
                return None
            
            backup_files = [f for f in os.listdir(self.backups_dir) if f.endswith('.json')]
            if not backup_files:
                return None
            
            # 按時間排序，取最新的備份
            backup_files.sort(reverse=True)
            latest_backup = os.path.join(self.backups_dir, backup_files[0])
            
            with open(latest_backup, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 驗證備份數據
            if self._validate_data_integrity(data):
                # 恢復到主文件
                shutil.copy2(latest_backup, self.users_file_path)
                self.logger.info(f"成功從備份恢復數據: {latest_backup}")
                return data
            else:
                self.logger.error(f"備份數據也損壞: {latest_backup}")
                return None
                
        except Exception as e:
            self.logger.error(f"從備份恢復失敗: {e}")
            return None
    
    def _create_default_structure(self) -> Dict:
        """創建預設的資料結構"""
        default_data = {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "version": "1.0",
                "total_users": 0,
                "container_id": os.environ.get('HOSTNAME', 'unknown'),
                "data_dir": self.data_dir
            },
            "users": {},
            "email_index": {},
            "name_index": {}
        }
        
        self._save_users(default_data)
        self.logger.info("創建預設用戶資料結構")
        return default_data
    
    def _save_users(self, data=None):
        """儲存用戶資料，包含原子寫入保護"""
        if data is None:
            data = self.users_data
        
        # 更新metadata
        data["metadata"]["last_updated"] = datetime.now().isoformat()
        data["metadata"]["total_users"] = len(data["users"])
        data["metadata"]["container_id"] = os.environ.get('HOSTNAME', 'unknown')
        
        # 原子寫入：先寫入臨時文件，再重命名
        temp_file = self.users_file_path + '.tmp'
        
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # 原子替換
            os.rename(temp_file, self.users_file_path)
            self.logger.info(f"用戶資料已儲存到 {self.users_file_path}")
            
        except Exception as e:
            self.logger.error(f"儲存用戶資料失敗: {e}")
            # 清理臨時文件
            if os.path.exists(temp_file):
                os.remove(temp_file)
            raise
    
    def _check_and_backup(self):
        """檢查並執行定期備份"""
        try:
            if not os.path.exists(self.users_file_path):
                return
            
            # 檢查最新備份時間
            backup_files = [f for f in os.listdir(self.backups_dir) if f.endswith('.json')]
            
            should_backup = True
            
            if backup_files:
                backup_files.sort(reverse=True)
                latest_backup = os.path.join(self.backups_dir, backup_files[0])
                
                # 檢查備份時間
                backup_time = os.path.getmtime(latest_backup)
                current_time = datetime.now().timestamp()
                hours_since_backup = (current_time - backup_time) / 3600
                
                should_backup = hours_since_backup >= self.backup_interval_hours
            
            if should_backup:
                self._create_backup()
                
        except Exception as e:
            self.logger.error(f"備份檢查失敗: {e}")
    
    def _create_backup(self):
        """創建數據備份"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"users_backup_{timestamp}.json"
            backup_path = os.path.join(self.backups_dir, backup_filename)
            
            shutil.copy2(self.users_file_path, backup_path)
            self.logger.info(f"創建備份: {backup_path}")
            
            # 清理舊備份（保留最近10個）
            self._cleanup_old_backups()
            
        except Exception as e:
            self.logger.error(f"創建備份失敗: {e}")
    
    def _cleanup_old_backups(self, keep_count=10):
        """清理舊備份文件"""
        try:
            backup_files = [f for f in os.listdir(self.backups_dir) if f.endswith('.json')]
            backup_files.sort(reverse=True)
            
            if len(backup_files) > keep_count:
                for old_backup in backup_files[keep_count:]:
                    old_backup_path = os.path.join(self.backups_dir, old_backup)
                    os.remove(old_backup_path)
                    self.logger.info(f"刪除舊備份: {old_backup}")
                    
        except Exception as e:
            self.logger.error(f"清理舊備份失敗: {e}")
    
    # 用戶管理API方法
    def add_user(self, line_id: str, name: str, email: str, **kwargs) -> bool:
        """新增用戶"""
        try:
            if line_id in self.users_data["users"]:
                self.logger.info(f"用戶 {line_id} 已存在，將更新資訊")
                return self.update_user(line_id, name=name, email=email, **kwargs)
            
            user_info = {
                "line_id": line_id,
                "name": name,
                "email": email,
                "created_at": datetime.now().isoformat(),
                "last_active": datetime.now().isoformat(),
                "interaction_count": 0,
                "status": "active",
                "container_registered": os.environ.get('HOSTNAME', 'unknown'),
                **kwargs
            }
            
            # 新增到主要資料
            self.users_data["users"][line_id] = user_info
            
            # 更新索引
            self.users_data["email_index"][email] = line_id
            self.users_data["name_index"][name] = line_id
            
            self._save_users()
            self.logger.info(f"成功新增用戶: {name} ({email})")
            return True
            
        except Exception as e:
            self.logger.error(f"新增用戶失敗: {e}")
            return False
    
    def get_user_by_line_id(self, line_id: str) -> Optional[Dict]:
        """根據LINE ID獲取用戶資訊"""
        try:
            user = self.users_data["users"].get(line_id)
            if user:
                # 更新最後活躍時間
                user["last_active"] = datetime.now().isoformat()
                user["interaction_count"] = user.get("interaction_count", 0) + 1
                self._save_users()
            return user
        except Exception as e:
            self.logger.error(f"獲取用戶資訊失敗: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """根據email獲取用戶資訊"""
        try:
            line_id = self.users_data["email_index"].get(email)
            if line_id:
                return self.get_user_by_line_id(line_id)
            return None
        except Exception as e:
            self.logger.error(f"根據email獲取用戶失敗: {e}")
            return None
    
    def get_user_by_name(self, name: str) -> Optional[Dict]:
        """根據姓名獲取用戶資訊"""
        try:
            line_id = self.users_data["name_index"].get(name)
            if line_id:
                return self.get_user_by_line_id(line_id)
            return None
        except Exception as e:
            self.logger.error(f"根據姓名獲取用戶失敗: {e}")
            return None
    
    def update_user(self, line_id: str, **kwargs) -> bool:
        """更新用戶資訊"""
        try:
            if line_id not in self.users_data["users"]:
                self.logger.warning(f"用戶 {line_id} 不存在")
                return False
            
            user = self.users_data["users"][line_id]
            old_email = user.get("email")
            old_name = user.get("name")
            
            # 更新用戶資訊
            for key, value in kwargs.items():
                user[key] = value
            
            user["updated_at"] = datetime.now().isoformat()
            
            # 更新索引
            new_email = kwargs.get("email")
            new_name = kwargs.get("name")
            
            if new_email and new_email != old_email:
                if old_email in self.users_data["email_index"]:
                    del self.users_data["email_index"][old_email]
                self.users_data["email_index"][new_email] = line_id
            
            if new_name and new_name != old_name:
                if old_name in self.users_data["name_index"]:
                    del self.users_data["name_index"][old_name]
                self.users_data["name_index"][new_name] = line_id
            
            self._save_users()
            self.logger.info(f"成功更新用戶: {line_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"更新用戶失敗: {e}")
            return False
    
    def delete_user(self, line_id: str) -> bool:
        """刪除用戶"""
        try:
            if line_id not in self.users_data["users"]:
                self.logger.warning(f"用戶 {line_id} 不存在")
                return False
            
            user = self.users_data["users"][line_id]
            email = user.get("email")
            name = user.get("name")
            
            # 從主要資料中刪除
            del self.users_data["users"][line_id]
            
            # 從索引中刪除
            if email in self.users_data["email_index"]:
                del self.users_data["email_index"][email]
            if name in self.users_data["name_index"]:
                del self.users_data["name_index"][name]
            
            self._save_users()
            self.logger.info(f"成功刪除用戶: {line_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"刪除用戶失敗: {e}")
            return False
    
    def search_users(self, query: str) -> List[Dict]:
        """搜尋用戶（按姓名或email）"""
        try:
            results = []
            query_lower = query.lower()
            
            for user in self.users_data["users"].values():
                if (query_lower in user.get("name", "").lower() or 
                    query_lower in user.get("email", "").lower()):
                    results.append(user)
            
            return results
        except Exception as e:
            self.logger.error(f"搜尋用戶失敗: {e}")
            return []
    
    def get_user_display_name(self, line_id: str) -> str:
        """獲取用戶顯示名稱"""
        try:
            user = self.users_data["users"].get(line_id)
            if user:
                return user.get("name", line_id)
            return line_id
        except Exception as e:
            self.logger.error(f"獲取用戶顯示名稱失敗: {e}")
            return line_id
    
    def get_user_email(self, line_id: str) -> Optional[str]:
        """獲取用戶email"""
        try:
            user = self.users_data["users"].get(line_id)
            if user:
                return user.get("email")
            return None
        except Exception as e:
            self.logger.error(f"獲取用戶email失敗: {e}")
            return None
    
    def is_registered_user(self, line_id: str) -> bool:
        """檢查是否為已註冊用戶"""
        try:
            return line_id in self.users_data["users"]
        except Exception as e:
            self.logger.error(f"檢查用戶註冊狀態失敗: {e}")
            return False
    
    def get_all_users(self) -> Dict:
        """獲取所有用戶資料"""
        try:
            return self.users_data["users"]
        except Exception as e:
            self.logger.error(f"獲取所有用戶資料失敗: {e}")
            return {}
    
    def get_statistics(self) -> Dict:
        """獲取用戶統計資訊"""
        try:
            users = self.users_data["users"]
            total_users = len(users)
            
            if total_users == 0:
                return {
                    "total_users": 0,
                    "active_users": 0,
                    "total_interactions": 0,
                    "container_id": os.environ.get('HOSTNAME', 'unknown'),
                    "data_dir": self.data_dir
                }
            
            active_users = sum(1 for user in users.values() 
                              if user.get("status") == "active")
            total_interactions = sum(user.get("interaction_count", 0) 
                                   for user in users.values())
            
            return {
                "total_users": total_users,
                "active_users": active_users,
                "inactive_users": total_users - active_users,
                "total_interactions": total_interactions,
                "avg_interactions": total_interactions / total_users if total_users > 0 else 0,
                "container_id": os.environ.get('HOSTNAME', 'unknown'),
                "data_dir": self.data_dir,
                "last_backup": self._get_last_backup_time()
            }
        except Exception as e:
            self.logger.error(f"獲取統計資訊失敗: {e}")
            return {"error": str(e)}
    
    def _get_last_backup_time(self) -> Optional[str]:
        """獲取最後備份時間"""
        try:
            backup_files = [f for f in os.listdir(self.backups_dir) if f.endswith('.json')]
            if backup_files:
                backup_files.sort(reverse=True)
                latest_backup = os.path.join(self.backups_dir, backup_files[0])
                backup_time = os.path.getmtime(latest_backup)
                return datetime.fromtimestamp(backup_time).isoformat()
            return None
        except Exception as e:
            self.logger.error(f"獲取最後備份時間失敗: {e}")
            return None
    
    def export_users_csv(self, output_file: str = None) -> bool:
        """匯出用戶資料為CSV"""
        try:
            import csv
            
            if output_file is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_file = os.path.join(self.backups_dir, f"users_export_{timestamp}.csv")
            
            users = self.users_data["users"]
            if not users:
                self.logger.warning("沒有用戶資料可匯出")
                return False
            
            # 獲取所有可能的欄位
            all_fields = set()
            for user in users.values():
                all_fields.update(user.keys())
            
            all_fields = sorted(list(all_fields))
            
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=all_fields)
                writer.writeheader()
                
                for user in users.values():
                    writer.writerow(user)
            
            self.logger.info(f"成功匯出 {len(users)} 個用戶資料到 {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"匯出CSV失敗: {e}")
            return False
    
    def force_backup(self) -> bool:
        """強制創建備份"""
        try:
            self._create_backup()
            return True
        except Exception as e:
            self.logger.error(f"強制備份失敗: {e}")
            return False
    
    def get_health_status(self) -> Dict:
        """獲取系統健康狀態"""
        try:
            return {
                "status": "healthy",
                "data_dir_exists": os.path.exists(self.data_dir),
                "users_file_exists": os.path.exists(self.users_file_path),
                "users_file_size": os.path.getsize(self.users_file_path) if os.path.exists(self.users_file_path) else 0,
                "backup_count": len([f for f in os.listdir(self.backups_dir) if f.endswith('.json')]),
                "last_backup": self._get_last_backup_time(),
                "container_id": os.environ.get('HOSTNAME', 'unknown'),
                "data_integrity": self._validate_data_integrity(self.users_data)
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "container_id": os.environ.get('HOSTNAME', 'unknown')
            }
