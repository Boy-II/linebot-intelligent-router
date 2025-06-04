import os
import json
import tempfile
from google.oauth2 import service_account

def get_google_credentials():
    """
    從環境變數或檔案載入 Google 憑證
    優先順序：環境變數 > 檔案路徑
    """
    # 方法 1：從環境變數載入 JSON 憑證
    credentials_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
    if credentials_json:
        try:
            # 解析 JSON 字串
            credentials_info = json.loads(credentials_json)
            
            # 創建臨時檔案
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
                json.dump(credentials_info, temp_file)
                temp_file_path = temp_file.name
            
            # 設定環境變數指向臨時檔案
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = temp_file_path
            
            print(f"✅ Google 憑證已從環境變數載入並寫入臨時檔案: {temp_file_path}")
            return service_account.Credentials.from_service_account_info(credentials_info)
            
        except json.JSONDecodeError as e:
            print(f"❌ 環境變數 GOOGLE_SERVICE_ACCOUNT_JSON 格式錯誤: {e}")
        except Exception as e:
            print(f"❌ 載入環境變數憑證失敗: {e}")
    
    # 方法 2：從 Base64 環境變數載入
    credentials_base64 = os.environ.get('GOOGLE_CREDENTIALS_BASE64')
    if credentials_base64:
        try:
            import base64
            # 解碼 Base64
            credentials_json = base64.b64decode(credentials_base64).decode('utf-8')
            credentials_info = json.loads(credentials_json)
            
            # 創建臨時檔案
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
                json.dump(credentials_info, temp_file)
                temp_file_path = temp_file.name
            
            # 設定環境變數指向臨時檔案
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = temp_file_path
            
            print(f"✅ Google 憑證已從 Base64 環境變數載入: {temp_file_path}")
            return service_account.Credentials.from_service_account_info(credentials_info)
            
        except Exception as e:
            print(f"❌ 載入 Base64 憑證失敗: {e}")
    
    # 方法 3：從檔案路徑載入
    credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    if credentials_path and os.path.exists(credentials_path):
        try:
            credentials = service_account.Credentials.from_service_account_file(credentials_path)
            print(f"✅ Google 憑證已從檔案載入: {credentials_path}")
            return credentials
        except Exception as e:
            print(f"❌ 載入檔案憑證失敗: {e}")
    
    # 如果都失敗，返回 None
    print("⚠️ 未找到有效的 Google 憑證")
    return None

def setup_google_credentials():
    """設定 Google 憑證，在應用程式啟動時呼叫"""
    credentials = get_google_credentials()
    if credentials:
        # 驗證憑證是否有效
        try:
            project_id = getattr(credentials, 'project_id', None)
            if project_id:
                print(f"✅ Google 憑證驗證成功，專案 ID: {project_id}")
            else:
                print("✅ Google 憑證載入成功")
            return True
        except Exception as e:
            print(f"❌ Google 憑證驗證失敗: {e}")
            return False
    return False

def get_project_id():
    """獲取 Google Cloud 專案 ID"""
    # 優先使用環境變數
    project_id = os.environ.get('DIALOGFLOW_PROJECT_ID')
    if project_id:
        return project_id
    
    # 嘗試從憑證中獲取
    credentials = get_google_credentials()
    if credentials and hasattr(credentials, 'project_id'):
        return credentials.project_id
    
    return None
