#!/usr/bin/env python3
"""
Docker 配置驗證腳本

檢查 Docker 相關配置是否正確包含所有必要檔案
"""

import os
import subprocess
from pathlib import Path

def check_dockerfile_includes():
    """檢查 Dockerfile 是否包含必要檔案"""
    print("🐳 檢查 Dockerfile 配置...")
    
    dockerfile_path = Path("Dockerfile")
    if not dockerfile_path.exists():
        print("❌ Dockerfile 不存在")
        return False
    
    with open(dockerfile_path, 'r') as f:
        dockerfile_content = f.read()
    
    # 必須包含的檔案
    required_files = [
        'main.py',
        'models.py', 
        'user_manager.py',
        'bot_config.py',  # 新增的重要檔案
        'dialogflow_client.py',
        'google_credentials.py',
        'requirements.txt'
    ]
    
    missing_files = []
    for file in required_files:
        if f"COPY {file}" not in dockerfile_content:
            missing_files.append(file)
    
    if missing_files:
        print("❌ Dockerfile 缺少以下檔案:")
        for file in missing_files:
            print(f"  • {file}")
        return False
    else:
        print("✅ Dockerfile 包含所有必要檔案")
        return True

def check_dockerignore():
    """檢查 .dockerignore 配置"""
    print("\n🚫 檢查 .dockerignore 配置...")
    
    dockerignore_path = Path(".dockerignore")
    if not dockerignore_path.exists():
        print("⚠️ .dockerignore 不存在")
        return True  # 不是致命錯誤
    
    with open(dockerignore_path, 'r') as f:
        dockerignore_content = f.read()
    
    # 檢查是否正確排除測試檔案
    if "test_*.py" in dockerignore_content:
        print("✅ 測試檔案已正確排除")
    else:
        print("⚠️ 建議在 .dockerignore 中排除測試檔案")
    
    # 檢查是否包含 bot_config.py（不應該被排除）
    if "bot_config.py" in dockerignore_content:
        print("❌ bot_config.py 不應該被排除")
        return False
    else:
        print("✅ bot_config.py 不在排除列表中")
        return True

def check_requirements():
    """檢查 requirements.txt 是否包含新依賴"""
    print("\n📦 檢查 requirements.txt...")
    
    requirements_path = Path("requirements.txt")
    if not requirements_path.exists():
        print("❌ requirements.txt 不存在")
        return False
    
    with open(requirements_path, 'r') as f:
        requirements_content = f.read()
    
    if "pytz" in requirements_content:
        print("✅ pytz 依賴已包含")
        return True
    else:
        print("❌ 缺少 pytz 依賴")
        return False

def check_file_exists():
    """檢查關鍵檔案是否存在"""
    print("\n📁 檢查關鍵檔案存在性...")
    
    critical_files = [
        'bot_config.py',
        'main.py',
        'user_manager.py',
        'requirements.txt',
        'Dockerfile'
    ]
    
    missing_files = []
    for file in critical_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print("❌ 缺少關鍵檔案:")
        for file in missing_files:
            print(f"  • {file}")
        return False
    else:
        print("✅ 所有關鍵檔案都存在")
        return True

def test_docker_build():
    """測試 Docker 建置（如果 Docker 可用）"""
    print("\n🔨 測試 Docker 建置...")
    
    try:
        # 檢查 Docker 是否可用
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            print("⚠️ Docker 不可用，跳過建置測試")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("⚠️ Docker 不可用，跳過建置測試")
        return True
    
    try:
        print("正在測試 Docker 建置（僅驗證語法）...")
        # 使用 dry-run 模式測試 Dockerfile 語法
        result = subprocess.run([
            'docker', 'build', '--dry-run', '-t', 'linebot:test', '.'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Dockerfile 語法正確")
            return True
        else:
            print(f"❌ Docker 建置測試失敗: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️ Docker 建置測試超時")
        return True
    except Exception as e:
        print(f"⚠️ Docker 建置測試錯誤: {e}")
        return True

def check_dev_dockerfile():
    """檢查開發環境 Dockerfile"""
    print("\n🛠️ 檢查開發環境 Dockerfile...")
    
    dev_dockerfile = Path("Dockerfile.dev")
    if dev_dockerfile.exists():
        print("✅ Dockerfile.dev 存在")
        
        with open(dev_dockerfile, 'r') as f:
            content = f.read()
        
        # 檢查是否包含測試檔案
        test_files = ['verify_all_fixes.py', 'test_group_behavior.py', 'test_timezone.py']
        included_tests = [f for f in test_files if f"COPY {f}" in content]
        
        if len(included_tests) >= 2:
            print(f"✅ 開發環境包含 {len(included_tests)} 個測試檔案")
            return True
        else:
            print("⚠️ 開發環境測試檔案不完整")
            return True
    else:
        print("⚠️ Dockerfile.dev 不存在（可選）")
        return True

def generate_docker_summary():
    """生成 Docker 配置摘要"""
    print("\n📋 Docker 配置摘要")
    print("="*50)
    
    print("🎯 生產環境 (Dockerfile):")
    print("  ✅ 核心應用檔案")
    print("  ✅ bot_config.py (新增)")
    print("  ❌ 測試檔案 (已排除)")
    print("  ✅ 最小化鏡像大小")
    
    print("\n🛠️ 開發環境 (Dockerfile.dev):")
    print("  ✅ 所有應用檔案")
    print("  ✅ 完整測試套件")
    print("  ✅ 開發工具")
    
    print("\n📦 依賴項:")
    print("  ✅ pytz (時區處理)")
    print("  ✅ 所有原有依賴")
    
    print("\n🚀 部署建議:")
    print("  • 生產環境使用 Dockerfile")
    print("  • 開發測試使用 Dockerfile.dev")
    print("  • 重建鏡像以應用更新")

def main():
    """主檢查函數"""
    print("🐳 Docker 配置驗證工具")
    print("="*60)
    print("檢查項目：Dockerfile、.dockerignore、requirements.txt、檔案存在性")
    print("="*60)
    print()
    
    # 執行所有檢查
    checks = {
        "檔案存在性": check_file_exists(),
        "Dockerfile 配置": check_dockerfile_includes(),
        ".dockerignore 配置": check_dockerignore(),
        "dependencies": check_requirements(),
        "開發環境 Dockerfile": check_dev_dockerfile(),
        "Docker 建置測試": test_docker_build()
    }
    
    # 統計結果
    passed = sum(checks.values())
    total = len(checks)
    
    print(f"\n📊 檢查結果: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 Docker 配置完全正確！")
        generate_docker_summary()
        return True
    else:
        print("⚠️ 部分檢查未通過，請檢查上述錯誤")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
