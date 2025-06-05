#!/usr/bin/env python3
"""
環境變數診斷工具

檢查環境變數是否有污染或格式問題
"""

import os
from dotenv import load_dotenv

def diagnose_environment():
    """診斷環境變數問題"""
    print("🔍 環境變數診斷工具")
    print("="*50)
    
    # 載入環境變數
    load_dotenv()
    
    # 檢查 .env 檔案格式
    print("\n📁 檢查 .env 檔案格式:")
    try:
        with open('.env', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines, 1):
            line = line.rstrip('\n\r')
            if 'DATABASE_URL' in line:
                print(f"  {i:2d}: {line}")
                # 檢查是否有多個環境變數在同一行
                if line.count('=') > 1:
                    print(f"      ❌ 發現多個 '=' 在同一行！")
                if 'BOT_NAME' in line:
                    print(f"      ❌ 發現 BOT_NAME 和 DATABASE_URL 在同一行！")
            elif 'BOT_NAME' in line:
                print(f"  {i:2d}: {line}")
                
    except FileNotFoundError:
        print("  ❌ .env 檔案不存在")
    
    # 檢查所有環境變數
    print("\n📋 所有環境變數:")
    for key, value in os.environ.items():
        if any(keyword in key.upper() for keyword in ['DATABASE', 'BOT', 'LINE', 'N8N']):
            # 隱藏敏感資訊
            if 'TOKEN' in key or 'SECRET' in key or 'PASSWORD' in key:
                display_value = value[:10] + "..." if len(value) > 10 else "***"
            else:
                display_value = value
            print(f"  {key} = {display_value}")
    
    print("\n🎯 重點檢查:")
    
    # 檢查 DATABASE_URL
    database_url = os.getenv('DATABASE_URL')
    print(f"\nDATABASE_URL:")
    if database_url:
        print(f"  ✅ 已設定: {database_url}")
        # 檢查格式
        if not database_url.startswith('postgresql'):
            print(f"  ❌ 格式異常: 不是有效的 PostgreSQL URL")
        if '=' in database_url and not database_url.startswith('postgresql'):
            print(f"  ❌ 可能包含環境變數污染")
    else:
        print(f"  ⚠️ 未設定，將使用預設值")
    
    # 檢查 BOT_NAME
    bot_name = os.getenv('BOT_NAME')
    print(f"\nBOT_NAME:")
    if bot_name:
        print(f"  ✅ 已設定: {bot_name}")
        if bot_name != '視覺設計組':
            print(f"  ⚠️ 預期值: 視覺設計組")
    else:
        print(f"  ❌ 未設定")
    
    # 檢查 TZ
    tz = os.getenv('TZ')
    print(f"\nTZ:")
    if tz:
        print(f"  ✅ 已設定: {tz}")
        if tz != 'Asia/Taipei':
            print(f"  ⚠️ 預期值: Asia/Taipei")
    else:
        print(f"  ⚠️ 未設定")
    
    # 構建推薦的 DATABASE_URL
    print(f"\n💡 推薦配置:")
    print(f"DATABASE_URL=postgresql://postgres:postgres@postgresql.zeabur.internal:5432/postgres")
    print(f"BOT_NAME=視覺設計組")
    print(f"TZ=Asia/Taipei")
    
    # 檢查是否有異常的環境變數
    print(f"\n🚨 異常檢查:")
    suspicious_vars = []
    database_url = os.getenv('DATABASE_URL', '')
    
    # 檢查 DATABASE_URL 是否包含其他變數
    if 'BOT_NAME' in database_url:
        print(f"  ❌ 發現 DATABASE_URL 包含 BOT_NAME！")
        print(f"      DATABASE_URL: {database_url}")
        suspicious_vars.append(('DATABASE_URL', '包含BOT_NAME'))
    
    if '=' in database_url and database_url.count('=') > 0:
        # 檢查是否有多個 '=' 號
        equal_count = database_url.count('=')
        if equal_count > 1 or (not database_url.startswith('postgresql') and '=' in database_url):
            print(f"  ❌ DATABASE_URL 格式異常：包含 {equal_count} 個 '=' 號")
            suspicious_vars.append(('DATABASE_URL', '格式異常'))
    
    for key, value in os.environ.items():
        if '=' in value and len(value) > 50 and not key in ['PATH', 'LS_COLORS']:
            suspicious_vars.append((key, value[:50] + "..."))
    
    if suspicious_vars:
        print("  發現可能有問題的環境變數:")
        for key, issue in suspicious_vars:
            if isinstance(issue, str) and len(issue) > 50:
                print(f"    {key}: {issue}")
            else:
                print(f"    {key}: {issue}")
    else:
        print("  ✅ 未發現異常環境變數")

def generate_env_fix():
    """生成修復後的 .env 建議"""
    print(f"\n🔧 建議的 .env 檔案內容:")
    print("-"*50)
    
    env_content = """# LINE Bot 基本配置
LINE_CHANNEL_ACCESS_TOKEN=your_token_here
LINE_CHANNEL_SECRET=your_secret_here

# n8n 整合
N8N_WEBHOOK_URL=https://bwen8n.zeabur.app/webhook/bwelinebotllm

# Bot 配置
BOT_NAME=視覺設計組

# 資料庫配置
DATABASE_URL=postgresql://postgres:postgres@postgresql.zeabur.internal:5432/postgres

# Dialogflow 配置
DIALOGFLOW_PROJECT_ID=bwe-line-webhook
GOOGLE_APPLICATION_CREDENTIALS=./credentials/bwe-line-webhook-c841c3ee149.json

# 系統配置
DATA_DIR=/app/data
LOG_LEVEL=INFO
TZ=Asia/Taipei
PYTHONUNBUFFERED=1

# Docker 配置
COMPOSE_PROJECT_NAME=linebot
"""
    
    print(env_content)

if __name__ == "__main__":
    diagnose_environment()
    generate_env_fix()
    
    print(f"\n🎯 下一步行動:")
    print(f"1. 檢查 Zeabur 部署環境中的環境變數設定")
    print(f"2. 確認 DATABASE_URL 格式正確")
    print(f"3. 重新部署應用程式")
    print(f"4. 檢查部署日誌確認問題解決")
