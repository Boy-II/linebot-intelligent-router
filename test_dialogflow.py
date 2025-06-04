#!/usr/bin/env python3
"""
Dialogflow 整合測試腳本
測試 bwe-line-webhook 專案的 Dialogflow 連接和功能
"""

import os
import asyncio
import json
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 設定環境變數
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './credentials/bwe-line-webhook-c841c3ee149e.json'
os.environ['DIALOGFLOW_PROJECT_ID'] = 'bwe-line-webhook'

def test_environment():
    """測試環境變數和憑證檔案"""
    print("=== 環境配置測試 ===")
    
    # 檢查環境變數
    project_id = os.environ.get('DIALOGFLOW_PROJECT_ID')
    credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    
    print(f"專案 ID: {project_id}")
    print(f"憑證路徑: {credentials_path}")
    
    # 檢查憑證檔案
    if os.path.exists(credentials_path):
        print("✅ 憑證檔案存在")
        
        # 嘗試讀取憑證檔案
        try:
            with open(credentials_path, 'r') as f:
                cred_data = json.load(f)
                print(f"✅ 憑證檔案有效，專案: {cred_data.get('project_id', 'unknown')}")
        except Exception as e:
            print(f"❌ 憑證檔案格式錯誤: {e}")
            return False
    else:
        print(f"❌ 憑證檔案不存在: {credentials_path}")
        return False
    
    return True

def test_google_cloud_connection():
    """測試 Google Cloud 連接"""
    print("\n=== Google Cloud 連接測試 ===")
    
    try:
        from google.cloud import dialogflow
        
        # 創建客戶端
        session_client = dialogflow.SessionsClient()
        project_id = os.environ.get('DIALOGFLOW_PROJECT_ID')
        
        # 測試會話路徑創建
        session_path = session_client.session_path(project_id, 'test-session')
        print(f"✅ 會話路徑創建成功: {session_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Google Cloud 連接失敗: {e}")
        return False

async def test_dialogflow_client():
    """測試自定義 Dialogflow 客戶端"""
    print("\n=== Dialogflow 客戶端測試 ===")
    
    try:
        from dialogflow_client import dialogflow_client
        
        # 測試意圖檢測
        test_cases = [
            "我要填表",
            "幫我畫一隻貓",
            "分析這個RSS https://example.com/rss",
            "查詢狀態",
            "你好",
            "不知道在說什麼"
        ]
        
        for test_text in test_cases:
            print(f"\n測試文本: '{test_text}'")
            
            result = await dialogflow_client.detect_intent(
                text=test_text,
                session_id="test-session-123"
            )
            
            print(f"  意圖: {result['intent']}")
            print(f"  信心度: {result['confidence']:.2f}")
            print(f"  參數: {result['parameters']}")
            print(f"  回應: {result.get('fulfillment_text', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Dialogflow 客戶端測試失敗: {e}")
        return False

async def test_real_dialogflow_api():
    """測試真實的 Dialogflow API 調用"""
    print("\n=== 真實 Dialogflow API 測試 ===")
    
    try:
        from google.cloud import dialogflow
        
        project_id = os.environ.get('DIALOGFLOW_PROJECT_ID')
        session_client = dialogflow.SessionsClient()
        session = session_client.session_path(project_id, 'test-real-session')
        
        # 測試簡單的文本檢測
        text_input = dialogflow.TextInput(text="我要填表", language_code="zh-TW")
        query_input = dialogflow.QueryInput(text=text_input)
        
        response = session_client.detect_intent(
            request={"session": session, "query_input": query_input}
        )
        
        result = response.query_result
        print(f"✅ API 調用成功")
        print(f"  檢測到的意圖: {result.intent.display_name}")
        print(f"  信心度: {result.intent_detection_confidence:.2f}")
        print(f"  回應文本: {result.fulfillment_text}")
        
        return True
        
    except Exception as e:
        print(f"❌ 真實 API 調用失敗: {e}")
        print("  這可能是因為:")
        print("  1. Dialogflow 專案未正確設定")
        print("  2. 憑證權限不足")
        print("  3. Dialogflow API 未啟用")
        print("  4. 網路連接問題")
        return False

def test_docker_environment():
    """測試 Docker 環境配置"""
    print("\n=== Docker 環境測試 ===")
    
    # 檢查 Dockerfile 是否包含憑證複製
    if os.path.exists('Dockerfile'):
        with open('Dockerfile', 'r') as f:
            dockerfile_content = f.read()
            
            if 'credentials/' in dockerfile_content:
                print("✅ Dockerfile 包含憑證目錄")
            else:
                print("⚠️  Dockerfile 可能未包含憑證目錄")
                print("    建議添加: COPY credentials/ /app/credentials/")
    
    # 檢查 docker-compose 配置
    compose_files = ['docker-compose.yml', 'docker-compose.oracle.yml']
    for compose_file in compose_files:
        if os.path.exists(compose_file):
            with open(compose_file, 'r') as f:
                compose_content = f.read()
                
                if 'credentials' in compose_content:
                    print(f"✅ {compose_file} 包含憑證配置")
                else:
                    print(f"⚠️  {compose_file} 可能未包含憑證配置")
    return True # 新增此行以確保函數返回一個值

async def main():
    """主測試函數"""
    print("🚀 開始 Dialogflow 整合測試")
    print("=" * 50)
    
    # 測試步驟
    tests = [
        ("環境配置", test_environment),
        ("Google Cloud 連接", test_google_cloud_connection),
        ("Dialogflow 客戶端", test_dialogflow_client),
        ("真實 API 調用", test_real_dialogflow_api),
        ("Docker 環境", test_docker_environment),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} 測試異常: {e}")
            results[test_name] = False
    
    # 總結
    print("\n" + "=" * 50)
    print("🎯 測試結果總結")
    print("=" * 50)
    
    for test_name, passed in results.items():
        status = "✅ 通過" if passed else "❌ 失敗"
        print(f"{test_name}: {status}")
    
    passed_count = sum(results.values())
    total_count = len(results)
    
    print(f"\n總計: {passed_count}/{total_count} 項測試通過")
    
    if passed_count == total_count:
        print("🎉 所有測試通過！Dialogflow 整合準備就緒")
    elif passed_count >= 3:
        print("⚠️  部分測試失敗，但基本功能可用")
    else:
        print("🚨 多項測試失敗，需要檢查配置")
    
    # 下一步建議
    print("\n📋 下一步建議:")
    if not results.get("環境配置", False):
        print("1. 確保憑證檔案正確放置在 ./credentials/ 目錄")
        print("2. 檢查 .env 檔案中的 Dialogflow 配置")
    
    if not results.get("真實 API 調用", False):
        print("3. 在 Google Cloud Console 檢查:")
        print("   - Dialogflow API 是否已啟用")
        print("   - 服務帳戶權限是否正確")
        print("   - 專案 ID 是否正確")
    
    if results.get("Dialogflow 客戶端", False):
        print("4. 可以開始測試 LINE Bot 整合")
        print("5. 在 Dialogflow Console 中建立意圖")

if __name__ == "__main__":
    asyncio.run(main())
