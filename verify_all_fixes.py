#!/usr/bin/env python3
"""
LINE Bot 完整驗證腳本

一次性驗證所有關鍵修復：
1. Bot Name 更新
2. 群組行為修復  
3. 時區配置修復
4. 環境變數完整性
"""

import os
import sys
from datetime import datetime
import pytz
from dotenv import load_dotenv

def check_environment_setup():
    """檢查基本環境設定"""
    print("🔧 檢查環境設定...")
    load_dotenv()
    
    issues = []
    
    # 檢查必需環境變數
    required_vars = [
        'LINE_CHANNEL_ACCESS_TOKEN',
        'LINE_CHANNEL_SECRET', 
        'N8N_WEBHOOK_URL',
        'BOT_NAME'
    ]
    
    for var in required_vars:
        if not os.getenv(var):
            issues.append(f"缺少環境變數: {var}")
    
    # 檢查 Bot name
    bot_name = os.getenv('BOT_NAME')
    if bot_name != '視覺設計組':
        issues.append(f"Bot name 錯誤: 預期 '視覺設計組', 實際 '{bot_name}'")
    
    # 檢查時區設定
    tz_env = os.getenv('TZ')
    if tz_env != 'Asia/Taipei':
        issues.append(f"時區環境變數錯誤: 預期 'Asia/Taipei', 實際 '{tz_env}'")
    
    if issues:
        print("❌ 環境設定問題:")
        for issue in issues:
            print(f"  • {issue}")
        return False

def check_docker_configuration():
    """檢查 Docker 配置"""
    print("\n🐳 檢查 Docker 配置...")
    
    try:
        from pathlib import Path
        
        # 檢查 Dockerfile 是否存在
        if not Path("Dockerfile").exists():
            print("❌ Dockerfile 不存在")
            return False
        
        # 檢查 Dockerfile 是否包含 bot_config.py
        with open("Dockerfile", 'r') as f:
            dockerfile_content = f.read()
        
        if "bot_config.py" not in dockerfile_content:
            print("❌ Dockerfile 缺少 bot_config.py")
            return False
        
        # 檢查 requirements.txt 是否包含 pytz
        if Path("requirements.txt").exists():
            with open("requirements.txt", 'r') as f:
                requirements = f.read()
            if "pytz" not in requirements:
                print("❌ requirements.txt 缺少 pytz")
                return False
        
        print("✅ Docker 配置正確")
        print("  • Dockerfile 存在")
        print("  • bot_config.py 已包含")
        print("  • pytz 依賴已包含")
        
        # 檢查開發環境 Dockerfile
        if Path("Dockerfile.dev").exists():
            print("  • Dockerfile.dev 存在")
        
        return True
        
    except Exception as e:
        print(f"❌ Docker 配置檢查錯誤: {e}")
        return False
    else:
        print("✅ 環境設定正確")
        return True

def check_bot_config():
    """檢查 Bot 配置"""
    print("\n🤖 檢查 Bot 配置...")
    
    try:
        from bot_config import bot_config
        
        # 檢查 bot name
        if bot_config.bot_name != '視覺設計組':
            print(f"❌ Bot 配置名稱錯誤: {bot_config.bot_name}")
            return False
        
        # 檢查 mention patterns
        expected_patterns = ['@視覺設計組', '@assistant']
        for pattern in expected_patterns:
            if pattern not in bot_config.mention_patterns:
                print(f"❌ 缺少 mention 模式: {pattern}")
                return False
        
        print("✅ Bot 配置正確")
        print(f"  • Bot 名稱: {bot_config.bot_name}")
        print(f"  • Mention 模式: {bot_config.mention_patterns}")
        return True
        
    except ImportError as e:
        print(f"❌ 無法導入 bot_config: {e}")
        return False

def check_timezone_config():
    """檢查時區配置"""
    print("\n🕐 檢查時區配置...")
    
    try:
        # 檢查 pytz 可用性
        taipei_tz = pytz.timezone('Asia/Taipei')
        current_time = datetime.now(taipei_tz)
        
        # 檢查時區偏移
        offset = current_time.utcoffset()
        offset_hours = offset.total_seconds() / 3600
        
        if offset_hours != 8:
            print(f"❌ 時區偏移錯誤: 預期 GMT+8, 實際 GMT+{offset_hours}")
            return False
        
        print("✅ 時區配置正確")
        print(f"  • 當前台北時間: {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"  • UTC 偏移: GMT+{int(offset_hours)}")
        return True
        
    except Exception as e:
        print(f"❌ 時區配置錯誤: {e}")
        return False

def check_group_behavior():
    """檢查群組行為邏輯"""
    print("\n👥 檢查群組行為邏輯...")
    
    try:
        from bot_config import bot_config
        
        # 測試案例
        test_cases = [
            ("@視覺設計組 你好", True, "新 Bot name mention"),
            ("@assistant 你好", True, "舊 Bot name mention (相容性)"),
            ("/health", True, "公開指令"),
            ("普通聊天", False, "一般訊息應被忽略"),
            ("/填表", False, "私人指令應被忽略")
        ]
        
        failed_tests = []
        
        for message, expected, description in test_cases:
            result = bot_config.should_respond_in_group(message)
            if result != expected:
                failed_tests.append(f"{description}: 預期 {expected}, 實際 {result}")
        
        if failed_tests:
            print("❌ 群組行為測試失敗:")
            for failure in failed_tests:
                print(f"  • {failure}")
            return False
        else:
            print("✅ 群組行為邏輯正確")
            return True
            
    except Exception as e:
        print(f"❌ 群組行為檢查錯誤: {e}")
        return False

def check_database_connection():
    """檢查資料庫連接"""
    print("\n🗄️ 檢查資料庫連接...")
    
    try:
        from models import test_connection
        
        if test_connection():
            print("✅ 資料庫連接正常")
            return True
        else:
            print("❌ 資料庫連接失敗")
            return False
            
    except Exception as e:
        print(f"❌ 資料庫檢查錯誤: {e}")
        return False

def check_user_manager():
    """檢查用戶管理器"""
    print("\n👤 檢查用戶管理器...")
    
    try:
        from user_manager import UserManager
        
        user_manager = UserManager()
        health_status = user_manager.get_health_status()
        
        if health_status.get('status') == 'healthy':
            print("✅ 用戶管理器正常")
            print(f"  • 時間戳記: {health_status.get('timestamp')}")
            print(f"  • 時區: {health_status.get('timezone')}")
            return True
        else:
            print(f"❌ 用戶管理器異常: {health_status}")
            return False
            
    except Exception as e:
        print(f"❌ 用戶管理器檢查錯誤: {e}")
        return False

def check_dependencies():
    """檢查依賴項"""
    print("\n📦 檢查依賴項...")
    
    required_packages = [
        ('flask', 'Flask'),
        ('linebot', 'LINE Bot SDK'),
        ('pytz', '時區處理'),
        ('sqlalchemy', 'SQLAlchemy ORM'),
        ('psycopg2', 'PostgreSQL 驅動'),
        ('dotenv', '環境變數載入')
    ]
    
    missing_packages = []
    
    for package, description in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(f"{package} ({description})")
    
    if missing_packages:
        print("❌ 缺少依賴項:")
        for package in missing_packages:
            print(f"  • {package}")
        return False
    else:
        print("✅ 所有依賴項已安裝")
        return True

def generate_summary(results):
    """生成檢查摘要"""
    print("\n" + "="*60)
    print("📋 LINE Bot 驗證摘要")
    print("="*60)
    
    total_checks = len(results)
    passed_checks = sum(results.values())
    
    print(f"\n📊 檢查結果: {passed_checks}/{total_checks} 通過")
    
    if passed_checks == total_checks:
        print("🎉 所有檢查通過！LINE Bot 已準備就緒")
        status = "✅ 通過"
    else:
        print("⚠️ 部分檢查未通過，需要修復")
        status = "❌ 需要修復"
    
    print(f"\n📋 詳細結果:")
    for check_name, passed in results.items():
        emoji = "✅" if passed else "❌"
        print(f"  {emoji} {check_name}")
    
    # 部署建議
    print(f"\n🚀 部署建議:")
    if passed_checks == total_checks:
        print("  • 可以安全部署")
        print("  • 建議先在測試環境驗證")
        print("  • 部署後進行功能測試")
    else:
        print("  • 修復失敗的檢查項目")
        print("  • 重新執行驗證腳本")
        print("  • 確認所有檢查通過後再部署")
    
    return status

def main():
    """主驗證函數"""
    print("🚀 LINE Bot 完整驗證工具")
    print("="*60)
    print("檢查項目：Bot Name、群組行為、時區、環境變數、資料庫、Docker")
    print("="*60)
    print()
    
    # 執行所有檢查
    results = {
        "環境設定": check_environment_setup(),
        "Bot 配置": check_bot_config(), 
        "時區配置": check_timezone_config(),
        "群組行為": check_group_behavior(),
        "依賴項": check_dependencies(),
        "資料庫連接": check_database_connection(),
        "用戶管理器": check_user_manager(),
        "Docker 配置": check_docker_configuration()
    }
    
    # 生成摘要
    status = generate_summary(results)
    
    # 返回適當的退出碼
    if all(results.values()):
        sys.exit(0)  # 成功
    else:
        sys.exit(1)  # 失敗

if __name__ == "__main__":
    main()
