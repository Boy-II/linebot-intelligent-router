#!/bin/bash

# GitHub 自動上傳腳本
# 使用方法：chmod +x upload_to_github.sh && ./upload_to_github.sh

echo "🚀 開始上傳 LINE Bot 項目到 GitHub..."

# 檢查是否在正確的目錄
if [ ! -f "main.py" ]; then
    echo "❌ 錯誤：請在 linebot 項目根目錄執行此腳本"
    exit 1
fi

# 檢查 Git 是否已安裝
if ! command -v git &> /dev/null; then
    echo "❌ 錯誤：Git 未安裝，請先安裝 Git"
    exit 1
fi

# 初始化 Git（如果需要）
if [ ! -d ".git" ]; then
    echo "📁 初始化 Git 倉庫..."
    git init
fi

# 設置用戶信息
echo "👤 設置 Git 用戶信息..."
git config user.name "Boy-II"
git config user.email "cosca68@gmail.com"

# 檢查是否已設置遠端倉庫
if ! git remote | grep -q origin; then
    echo "🔗 添加 GitHub 遠端倉庫..."
    read -p "請輸入 GitHub 倉庫 URL (例如: https://github.com/Boy-II/linebot-intelligent-router.git): " REPO_URL
    git remote add origin "$REPO_URL"
else
    echo "✅ 遠端倉庫已設置"
fi

# 檢查 .gitignore 是否存在
if [ ! -f ".gitignore" ]; then
    echo "📄 創建 .gitignore 文件..."
    cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
.venv/
venv/
ENV/
env/

# Environment Variables
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# macOS
.DS_Store

# Google Cloud credentials
*.json
credentials/

# Logs
*.log

# Temporary files
tmp/
temp/
EOF
fi

# 檢查敏感文件
echo "🔒 檢查敏感文件..."
SENSITIVE_FILES=(
    ".env"
    "credentials.json"
    "service-account.json"
)

for file in "${SENSITIVE_FILES[@]}"; do
    if [ -f "$file" ] && ! grep -q "$file" .gitignore; then
        echo "⚠️  警告：發現敏感文件 $file，已自動添加到 .gitignore"
        echo "$file" >> .gitignore
    fi
done

# 添加所有文件
echo "📦 添加文件到 Git..."
git add .

# 檢查是否有文件要提交
if git diff --staged --quiet; then
    echo "ℹ️  沒有新的變更要提交"
else
    # 創建提交
    echo "💾 創建提交..."
    git commit -m "Initial commit: Multi-layer intelligent LINE Bot

Features:
- Flask routing with command detection  
- Dialogflow integration for natural language understanding
- n8n workflow integration for AI processing
- RSS analysis, image generation, and form handling
- Optimized architecture with AI processing centralized in n8n

Files included:
- main_optimized.py (recommended version)
- main_enhanced.py (full-featured version)
- main.py (original version)
- dialogflow_client.py (Dialogflow integration)
- n8n_workflow_guide.md (complete n8n setup guide)
- Various README files and configurations"
fi

# 推送到 GitHub
echo "🚀 推送到 GitHub..."
if git push -u origin main 2>/dev/null; then
    echo "✅ 成功上傳到 GitHub！"
    echo "🌐 你的倉庫地址：$(git remote get-url origin)"
else
    echo "⚠️  推送失敗，可能是因為："
    echo "   1. 遠端倉庫不存在（請先在 GitHub 創建倉庫）"
    echo "   2. 認證失敗（請檢查 GitHub 憑證）"
    echo "   3. 分支名稱問題（嘗試 git push -u origin master）"
    
    echo ""
    echo "📋 手動推送命令："
    echo "   git push -u origin main"
    echo "   或者："
    echo "   git push -u origin master"
fi

echo ""
echo "🎉 上傳腳本執行完成！"
echo ""
echo "📝 後續步驟："
echo "   1. 在 GitHub 檢查文件是否正確上傳"
echo "   2. 設置環境變數（不要上傳 .env 文件）"
echo "   3. 閱讀 README_Optimized.md 了解使用方法"
echo "   4. 參考 n8n_workflow_guide.md 設置工作流"
