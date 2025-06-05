#!/usr/bin/env python3
"""
LINE Bot 環境變數完整性檢查工具

此腳本會檢查所有必需和建議的環境變數，並提供詳細的配置建議。
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

class EnvironmentChecker:
    def __init__(self):
        self.missing_required = []
        self.missing_optional = []
        self.invalid_values = []
        self.warnings = []
        self.recommendations = []
        
    def check_required_vars(self):
        """檢查必需的環境變數"""
        print("🔍 檢查必需環境變數...")
        
        required_vars = {
            # LINE Bot 基本配置
            'LINE_CHANNEL_ACCESS_TOKEN': {
                'description': 'LINE Bot Channel Access Token',
                'validation': lambda x: x and len(x) > 50,
                'error_msg': '應該是一個長字串（通常超過100字元）'
            },
            'LINE_CHANNEL_SECRET': {
                'description': 'LINE Bot Channel Secret', 
                'validation': lambda x: x and len(x) >= 32,
                'error_msg': '應該是32字元的十六進制字串'
            },
            
            # n8n 整合
            'N8N_WEBHOOK_URL': {
                'description': 'n8n Webhook URL',
                'validation': lambda x: x and x.startswith(('http://', 'https://')),
                'error_msg': '應該是有效的 HTTP/HTTPS URL'
            },
            
            # Bot 配置
            'BOT_NAME': {
                'description': 'Bot 顯示名稱',
                'validation': lambda x: x and len(x.strip()) > 0,
                'error_msg': '不能為空'
            }
        }
        
        for var_name, config in required_vars.items():
            value = os.getenv(var_name)
            
            if not value:
                self.missing_required.append({
                    'name': var_name,
                    'description': config['description'],
                    'status': '❌ 缺少'
                })
            elif not config['validation'](value):
                self.invalid_values.append({
                    'name': var_name,
                    'description': config['description'],
                    'error': config['error_msg'],
                    'current_value': f"{value[:20]}..." if len(value) > 20 else value
                })
            else:
                print(f"  ✅ {var_name}: {config['description']}")
    
    def check_optional_vars(self):
        """檢查可選但建議的環境變數"""
        print("\n🔍 檢查建議環境變數...")
        
        optional_vars = {
            # Dialogflow 配置
            'DIALOGFLOW_PROJECT_ID': {
                'description': 'Dialogflow 專案 ID',
                'importance': 'high',
                'reason': '用於智能對話功能'
            },
            'GOOGLE_APPLICATION_CREDENTIALS': {
                'description': 'Google 服務帳戶憑證路徑',
                'importance': 'high',
                'reason': 'Dialogflow 認證必需'
            },
            'GOOGLE_SERVICE_ACCOUNT_JSON': {
                'description': 'Google 服務帳戶 JSON（適用於雲端部署）',
                'importance': 'high',
                'reason': '雲端部署時的認證方式'
            },
            'GOOGLE_CREDENTIALS_BASE64': {
                'description': 'Google 憑證 Base64 編碼',
                'importance': 'medium',
                'reason': '替代的認證方式'
            },
            
            # 資料庫配置
            'DATABASE_URL': {
                'description': '資料庫連接 URL',
                'importance': 'high',
                'reason': '用戶資料存儲'
            },
            'POSTGRES_HOST': {
                'description': 'PostgreSQL 主機',
                'importance': 'medium',
                'reason': '資料庫連接配置'
            },
            'POSTGRES_PORT': {
                'description': 'PostgreSQL 埠號',
                'importance': 'low',
                'reason': '預設為 5432'
            },
            'POSTGRES_DATABASE': {
                'description': 'PostgreSQL 資料庫名稱',
                'importance': 'medium',
                'reason': '資料庫連接配置'
            },
            'POSTGRES_USERNAME': {
                'description': 'PostgreSQL 用戶名',
                'importance': 'medium',
                'reason': '資料庫認證'
            },
            'POSTGRES_PASSWORD': {
                'description': 'PostgreSQL 密碼',
                'importance': 'medium',
                'reason': '資料庫認證'
            },
            
            # 應用程式配置
            'LOG_LEVEL': {
                'description': '日誌級別',
                'importance': 'low',
                'reason': '預設為 INFO'
            },
            'DATA_DIR': {
                'description': '資料目錄路徑',
                'importance': 'medium',
                'reason': '檔案存儲位置'
            },
            'WEBHOOK_TIMEOUT': {
                'description': 'Webhook 超時時間（秒）',
                'importance': 'low',
                'reason': '預設為 30 秒'
            },
            'MAX_RETRY_ATTEMPTS': {
                'description': '最大重試次數',
                'importance': 'low',
                'reason': '預設為 3 次'
            },
            'BACKUP_INTERVAL_HOURS': {
                'description': '備份間隔（小時）',
                'importance': 'low',
                'reason': '預設為 24 小時'
            },
            
            # Docker 配置
            'COMPOSE_PROJECT_NAME': {
                'description': 'Docker Compose 專案名稱',
                'importance': 'low',
                'reason': 'Docker 部署識別'
            },
            'PYTHONUNBUFFERED': {
                'description': 'Python 無緩衝輸出',
                'importance': 'low',
                'reason': 'Docker 日誌即時顯示'
            },
            
            # 開發配置
            'DEBUG': {
                'description': '調試模式',
                'importance': 'low',
                'reason': '開發環境使用'
            },
            'DEVELOPMENT_MODE': {
                'description': '開發模式',
                'importance': 'low',
                'reason': '開發環境特殊行為'
            }
        }
        
        for var_name, config in optional_vars.items():
            value = os.getenv(var_name)
            importance_emoji = {
                'high': '🔴',
                'medium': '🟡', 
                'low': '🟢'
            }[config['importance']]
            
            if not value:
                self.missing_optional.append({
                    'name': var_name,
                    'description': config['description'],
                    'importance': config['importance'],
                    'reason': config['reason'],
                    'emoji': importance_emoji
                })
            else:
                print(f"  ✅ {var_name}: {config['description']}")
    
    def check_google_credentials(self):
        """特別檢查 Google 憑證配置"""
        print("\n🔍 檢查 Google 憑證配置...")
        
        cred_file = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        cred_json = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')
        cred_base64 = os.getenv('GOOGLE_CREDENTIALS_BASE64')
        
        if cred_file:
            if Path(cred_file).exists():
                print(f"  ✅ 找到憑證檔案: {cred_file}")
                # 驗證 JSON 格式
                try:
                    with open(cred_file, 'r') as f:
                        json.load(f)
                    print("  ✅ 憑證檔案格式正確")
                except Exception as e:
                    self.invalid_values.append({
                        'name': 'GOOGLE_APPLICATION_CREDENTIALS',
                        'description': '憑證檔案格式錯誤',
                        'error': str(e)
                    })
            else:
                self.invalid_values.append({
                    'name': 'GOOGLE_APPLICATION_CREDENTIALS',
                    'description': '憑證檔案不存在',
                    'error': f'找不到檔案: {cred_file}'
                })
        
        elif cred_json:
            try:
                json.loads(cred_json)
                print("  ✅ Google 服務帳戶 JSON 格式正確")
            except Exception as e:
                self.invalid_values.append({
                    'name': 'GOOGLE_SERVICE_ACCOUNT_JSON',
                    'description': 'JSON 格式錯誤',
                    'error': str(e)
                })
        
        elif cred_base64:
            try:
                import base64
                decoded = base64.b64decode(cred_base64)
                json.loads(decoded)
                print("  ✅ Google 憑證 Base64 解碼成功")
            except Exception as e:
                self.invalid_values.append({
                    'name': 'GOOGLE_CREDENTIALS_BASE64',
                    'description': 'Base64 解碼或 JSON 格式錯誤',
                    'error': str(e)
                })
        
        else:
            self.warnings.append("未設定任何 Google 憑證，Dialogflow 功能將無法使用")
    
    def check_database_config(self):
        """檢查資料庫配置"""
        print("\n🔍 檢查資料庫配置...")
        
        database_url = os.getenv('DATABASE_URL')
        
        if database_url:
            print(f"  ✅ 資料庫 URL: {database_url[:30]}...")
            
            # 檢查 URL 格式
            if not database_url.startswith('postgresql://'):
                self.warnings.append("資料庫 URL 格式建議使用 postgresql://")
            
            # 測試連接
            try:
                from models import test_connection
                if test_connection():
                    print("  ✅ 資料庫連接測試成功")
                else:
                    self.warnings.append("資料庫連接測試失敗")
            except Exception as e:
                self.warnings.append(f"資料庫連接測試錯誤: {e}")
        else:
            # 檢查分離的配置
            host = os.getenv('POSTGRES_HOST')
            port = os.getenv('POSTGRES_PORT', '5432')
            database = os.getenv('POSTGRES_DATABASE')
            username = os.getenv('POSTGRES_USERNAME')
            password = os.getenv('POSTGRES_PASSWORD')
            
            if all([host, database, username, password]):
                constructed_url = f"postgresql://{username}:***@{host}:{port}/{database}"
                print(f"  ✅ 可構建資料庫 URL: {constructed_url}")
            else:
                self.warnings.append("缺少資料庫配置，將使用預設設定")
    
    def generate_recommendations(self):
        """生成配置建議"""
        print("\n💡 配置建議...")
        
        # 基於缺少的配置生成建議
        if any(var['importance'] == 'high' for var in self.missing_optional):
            self.recommendations.append("建議設定高優先級的環境變數以啟用完整功能")
        
        if not os.getenv('DATABASE_URL') and not all([
            os.getenv('POSTGRES_HOST'),
            os.getenv('POSTGRES_DATABASE'), 
            os.getenv('POSTGRES_USERNAME'),
            os.getenv('POSTGRES_PASSWORD')
        ]):
            self.recommendations.append("建議設定完整的資料庫配置")
        
        if not any([
            os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
            os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON'),
            os.getenv('GOOGLE_CREDENTIALS_BASE64')
        ]):
            self.recommendations.append("建議設定 Google 憑證以啟用 Dialogflow 功能")
        
        # 根據部署環境給出建議
        if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
            self.recommendations.append("本地開發使用檔案路徑認證，雲端部署建議使用環境變數")
        
        for rec in self.recommendations:
            print(f"  💡 {rec}")
    
    def print_summary(self):
        """列印檢查摘要"""
        print("\n" + "="*60)
        print("📋 環境變數檢查摘要")
        print("="*60)
        
        # 必需變數狀態
        if self.missing_required:
            print(f"\n❌ 缺少必需環境變數 ({len(self.missing_required)} 個):")
            for var in self.missing_required:
                print(f"  • {var['name']}: {var['description']}")
        
        if self.invalid_values:
            print(f"\n⚠️  環境變數值有問題 ({len(self.invalid_values)} 個):")
            for var in self.invalid_values:
                print(f"  • {var['name']}: {var.get('error', '格式錯誤')}")
        
        # 可選變數狀態
        if self.missing_optional:
            print(f"\n📋 缺少可選環境變數 ({len(self.missing_optional)} 個):")
            
            # 按重要性分組
            by_importance = {}
            for var in self.missing_optional:
                importance = var['importance']
                if importance not in by_importance:
                    by_importance[importance] = []
                by_importance[importance].append(var)
            
            for importance in ['high', 'medium', 'low']:
                if importance in by_importance:
                    print(f"\n  {importance.upper()} 優先級:")
                    for var in by_importance[importance]:
                        print(f"    {var['emoji']} {var['name']}: {var['description']}")
                        print(f"       理由: {var['reason']}")
        
        # 警告
        if self.warnings:
            print(f"\n⚠️  警告 ({len(self.warnings)} 個):")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        # 整體狀態
        print(f"\n🏁 檢查完成:")
        if not self.missing_required and not self.invalid_values:
            print("  ✅ 所有必需環境變數已正確設定")
        else:
            print(f"  ❌ 發現 {len(self.missing_required + self.invalid_values)} 個問題需要解決")
        
        high_priority_missing = sum(1 for var in self.missing_optional if var['importance'] == 'high')
        if high_priority_missing > 0:
            print(f"  🔴 建議設定 {high_priority_missing} 個高優先級環境變數")
    
    def generate_env_template(self):
        """生成 .env 範本"""
        current_env = {}
        try:
            with open('.env', 'r') as f:
                for line in f:
                    if '=' in line and not line.strip().startswith('#'):
                        key, value = line.strip().split('=', 1)
                        current_env[key] = value
        except FileNotFoundError:
            pass
        
        print(f"\n📝 建議的 .env 檔案內容:")
        print("# " + "="*50)
        print("# LINE Bot 環境變數配置")
        print("# " + "="*50)
        
        # 顯示當前配置和建議
        all_vars = [
            ('LINE_CHANNEL_ACCESS_TOKEN', '必需', 'your_line_channel_access_token'),
            ('LINE_CHANNEL_SECRET', '必需', 'your_line_channel_secret'),
            ('N8N_WEBHOOK_URL', '必需', 'https://your-n8n.domain.com/webhook/linebot'),
            ('BOT_NAME', '必需', '視覺設計組'),
            ('DIALOGFLOW_PROJECT_ID', '建議', 'your-dialogflow-project'),
            ('GOOGLE_APPLICATION_CREDENTIALS', '建議', './credentials/service-account.json'),
            ('DATABASE_URL', '建議', 'postgresql://user:pass@host:5432/db'),
            ('LOG_LEVEL', '可選', 'INFO'),
            ('WEBHOOK_TIMEOUT', '可選', '30'),
            ('MAX_RETRY_ATTEMPTS', '可選', '3'),
        ]
        
        for var_name, priority, default in all_vars:
            current_value = current_env.get(var_name, '')
            if current_value:
                # 隱藏敏感資訊
                if 'TOKEN' in var_name or 'SECRET' in var_name or 'PASSWORD' in var_name:
                    display_value = current_value[:10] + '...' if len(current_value) > 10 else '***'
                else:
                    display_value = current_value
                print(f"{var_name}={display_value}  # {priority} - ✅ 已設定")
            else:
                print(f"# {var_name}={default}  # {priority} - ❌ 需要設定")

def main():
    """主函數"""
    print("🔧 LINE Bot 環境變數檢查工具")
    print("="*60)
    
    checker = EnvironmentChecker()
    
    # 執行各項檢查
    checker.check_required_vars()
    checker.check_optional_vars()
    checker.check_google_credentials()
    checker.check_database_config()
    checker.generate_recommendations()
    
    # 顯示摘要
    checker.print_summary()
    
    # 生成 .env 範本
    if checker.missing_required or checker.invalid_values:
        checker.generate_env_template()
    
    # 返回狀態碼
    if checker.missing_required or checker.invalid_values:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
