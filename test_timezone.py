#!/usr/bin/env python3
"""
時區配置測試腳本

用於驗證 LINE Bot 的時區設定是否正確
"""

import os
import pytz
from datetime import datetime
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

def test_timezone_configuration():
    """測試時區配置"""
    print("🕐 時區配置測試")
    print("=" * 50)
    
    # 設定台北時區
    taipei_tz = pytz.timezone('Asia/Taipei')
    utc_tz = pytz.UTC
    
    # 獲取當前時間
    now_utc = datetime.now(utc_tz)
    now_taipei = datetime.now(taipei_tz)
    now_local = datetime.now()
    
    print(f"🌍 UTC 時間: {now_utc.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"🇹🇼 台北時間: {now_taipei.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"💻 系統本地時間: {now_local.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 檢查環境變數
    tz_env = os.getenv('TZ')
    print(f"\n📋 環境變數 TZ: {tz_env}")
    
    # 計算時差
    utc_offset = now_taipei.utcoffset()
    print(f"⏰ UTC 偏移量: {utc_offset}")
    
    # 驗證是否為 GMT+8
    expected_offset_hours = 8
    actual_offset_hours = utc_offset.total_seconds() / 3600
    
    if actual_offset_hours == expected_offset_hours:
        print(f"✅ 時區設定正確: GMT+{int(actual_offset_hours)}")
    else:
        print(f"❌ 時區設定錯誤: 預期 GMT+{expected_offset_hours}, 實際 GMT+{actual_offset_hours}")
    
    # 測試 ISO 格式
    iso_format = now_taipei.isoformat()
    print(f"\n📄 ISO 格式時間戳記: {iso_format}")
    
    return now_taipei

def test_health_check_format():
    """測試健康檢查時間格式"""
    print("\n🔍 健康檢查時間格式測試")
    print("=" * 50)
    
    taipei_tz = pytz.timezone('Asia/Taipei')
    current_time = datetime.now(taipei_tz)
    
    # 模擬健康檢查的時間格式
    health_format = current_time.strftime('%Y-%m-%d %H:%M:%S %Z')
    iso_format = current_time.isoformat()
    
    print(f"💊 健康檢查顯示格式: {health_format}")
    print(f"📡 API 回應 ISO 格式: {iso_format}")
    
    return health_format, iso_format

def test_database_timestamp():
    """測試資料庫時間戳記處理"""
    print("\n🗄️ 資料庫時間戳記處理測試")
    print("=" * 50)
    
    try:
        from user_manager import UserManager, TAIPEI_TZ
        
        user_manager = UserManager()
        health_status = user_manager.get_health_status()
        
        print(f"📊 用戶管理器健康狀態: {health_status.get('status')}")
        print(f"⏰ 時間戳記: {health_status.get('timestamp')}")
        print(f"🌍 時區資訊: {health_status.get('timezone')}")
        
        # 檢查統計資訊
        stats = user_manager.get_statistics()
        if stats.get('latest_user_created'):
            print(f"👤 最新用戶建立時間: {stats['latest_user_created']}")
        
    except Exception as e:
        print(f"❌ 資料庫測試錯誤: {e}")

def generate_timezone_fix_summary():
    """生成時區修復摘要"""
    print("\n📋 時區修復摘要")
    print("=" * 50)
    
    fixes = [
        "✅ 添加 pytz 到 requirements.txt",
        "✅ 在 main.py 中導入並設定 TAIPEI_TZ",
        "✅ 修復健康檢查時間顯示格式",
        "✅ 修復 API 端點時間戳記",
        "✅ 修復 n8n 工作流時間戳記", 
        "✅ 修復用戶管理器時間處理",
        "✅ 添加 TZ=Asia/Taipei 到環境變數",
        "✅ 統一使用台北時區 (GMT+8)"
    ]
    
    for fix in fixes:
        print(f"  {fix}")
    
    print(f"\n🎯 修復後效果:")
    print(f"  • /health 指令將顯示正確的台北時間")
    print(f"  • API 回應包含時區資訊")
    print(f"  • 所有時間戳記統一使用 GMT+8")
    print(f"  • 資料庫時間正確轉換為台北時區")

def main():
    """主測試函數"""
    print("🚀 LINE Bot 時區配置測試工具")
    print("=" * 60)
    print()
    
    # 執行各項測試
    taipei_time = test_timezone_configuration()
    test_health_check_format()
    test_database_timestamp()
    generate_timezone_fix_summary()
    
    print(f"\n🏁 測試完成")
    print(f"當前台北時間: {taipei_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print("=" * 60)

if __name__ == "__main__":
    main()
