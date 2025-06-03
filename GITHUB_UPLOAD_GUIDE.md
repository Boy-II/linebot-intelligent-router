# GitHub 上傳指南

## 步驟1：在 GitHub 創建私人倉庫

1. 前往 https://github.com/Boy-II
2. 點擊 "New repository" 按鈕
3. 填寫倉庫資訊：
   - **Repository name**: `linebot-intelligent-router`
   - **Description**: `A multi-layer intelligent LINE Bot with Flask routing and n8n workflow integration`
   - **Visibility**: 選擇 "Private"
   - **Initialize repository**: 不要勾選任何選項（因為我們要上傳現有代碼）

## 步驟2：準備本地 Git 設置

在你的終端中執行以下命令：

```bash
cd /Volumes/M200/project/linebot

# 初始化 Git（如果還沒有的話）
git init

# 設置用戶信息
git config user.name "Boy-II"
git config user.email "cosca68@gmail.com"

# 添加 GitHub 遠端倉庫
git remote add origin https://github.com/Boy-II/linebot-intelligent-router.git
```

## 步驟3：創建 .gitignore（如果需要更新）

確保 .gitignore 包含以下內容：

```
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
.env.enhanced
.env.optimized

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
```

## 步驟4：提交和推送代碼

```bash
# 添加所有文件
git add .

# 創建初始提交
git commit -m "Initial commit: Multi-layer intelligent LINE Bot

Features:
- Flask routing with command detection
- Dialogflow integration for natural language understanding  
- n8n workflow integration for AI processing
- RSS analysis, image generation, and form handling
- Optimized architecture with AI processing centralized in n8n"

# 推送到 GitHub
git push -u origin main
```

## 步驟5：驗證上傳

1. 前往 https://github.com/Boy-II/linebot-intelligent-router
2. 確認所有文件都已上傳
3. 檢查 README 顯示是否正常

## 項目結構說明

上傳後的項目將包含：

### 核心文件
- `main_optimized.py` - 優化版主程式（推薦使用）
- `main_enhanced.py` - 增強版主程式  
- `main.py` - 原始版本
- `dialogflow_client.py` - Dialogflow 整合模組

### 配置文件
- `requirements_optimized.txt` - 優化版依賴（推薦）
- `Dockerfile.optimized` - 優化版容器配置
- `.env.optimized` - 環境變數範例

### 文檔
- `README_Optimized.md` - 優化版說明（主要文檔）
- `n8n_workflow_guide.md` - n8n 工作流設計指南
- `README_Enhanced.md` - 增強版說明

## 安全提醒

⚠️ **重要**：確保以下敏感信息不會被上傳：
- `.env` 文件（包含真實的 API keys）
- Google Cloud 服務帳號 JSON 文件
- 任何包含密碼或 tokens 的文件

所有敏感配置都應該在 Cloud Run 等部署環境中通過環境變數設置。

## 後續步驟

1. **設置 GitHub Actions**（可選）：自動化部署到 Cloud Run
2. **添加 Collaborators**：如果需要團隊協作
3. **設置 Branch Protection**：保護主分支
4. **創建 Issues 和 Projects**：追蹤開發進度
