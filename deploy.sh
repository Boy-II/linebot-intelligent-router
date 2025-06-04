#!/bin/bash

# LINE Bot Docker 部署腳本
# 支援數據持久化和容器管理

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函數定義
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 檢查必要文件
check_requirements() {
    log_info "檢查部署需求..."
    
    # 檢查 Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安裝，請先安裝 Docker"
        exit 1
    fi
    
    # 檢查 Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安裝，請先安裝 Docker Compose"
        exit 1
    fi
    
    # 檢查必要文件
    required_files=("main.py" "user_manager.py" "requirements.txt" "Dockerfile")
    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            log_error "缺少必要文件: $file"
            exit 1
        fi
    done
    
    log_success "需求檢查通過"
}

# 創建數據目錄
setup_data_directories() {
    log_info "設置數據目錄..."
    
    # 創建本地數據目錄
    mkdir -p ./data/users
    mkdir -p ./data/backups
    mkdir -p ./data/logs
    
    # 設定權限
    chmod -R 755 ./data
    
    # 如果有初始用戶數據，複製到正確位置
    if [[ -f "./data/users/users.json" ]]; then
        log_info "發現現有用戶數據"
    else
        log_warning "未發現用戶數據，將使用預設結構"
    fi
    
    log_success "數據目錄設置完成"
}

# 創建環境變數文件
setup_environment() {
    if [[ ! -f ".env" ]]; then
        log_warning "未找到 .env 文件，創建範例文件..."
        cat > .env << EOF
# LINE Bot 基本配置
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token
LINE_CHANNEL_SECRET=your_line_channel_secret

# n8n 工作流配置
N8N_WEBHOOK_URL=http://localhost:5678/webhook/line-bot-unified

# Bot 行為配置
BOT_NAME=assistant

# Dialogflow 配置（可選）
DIALOGFLOW_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/service-account.json

# 數據持久化配置
DATA_DIR=/app/data
BACKUP_INTERVAL_HOURS=24

# 日誌配置
LOG_LEVEL=INFO

# Docker 配置
COMPOSE_PROJECT_NAME=linebot
EOF
        log_warning "請編輯 .env 文件設定您的配置"
        return 1
    fi
    
    log_success "環境變數檢查完成"
    return 0
}

# 構建 Docker 映像
build_image() {
    log_info "構建 Docker 映像..."
    
    docker build -t linebot:latest .
    
    if [[ $? -eq 0 ]]; then
        log_success "Docker 映像構建成功"
    else
        log_error "Docker 映像構建失敗"
        exit 1
    fi
}

# 部署服務
deploy_services() {
    log_info "部署服務..."
    
    # 停止現有服務
    docker-compose down
    
    # 啟動服務
    docker-compose up -d
    
    if [[ $? -eq 0 ]]; then
        log_success "服務部署成功"
    else
        log_error "服務部署失敗"
        exit 1
    fi
}

# 等待服務啟動
wait_for_services() {
    log_info "等待服務啟動..."
    
    # 等待健康檢查通過
    for i in {1..30}; do
        if curl -f http://localhost:8080/health &> /dev/null; then
            log_success "服務健康檢查通過"
            return 0
        fi
        echo -n "."
        sleep 2
    done
    
    log_error "服務啟動超時"
    return 1
}

# 顯示狀態
show_status() {
    log_info "服務狀態："
    docker-compose ps
    
    echo ""
    log_info "服務端點："
    echo "  - 健康檢查: http://localhost:8080/health"
    echo "  - 用戶API: http://localhost:8080/api/users"
    echo "  - 統計API: http://localhost:8080/api/users/stats"
    
    echo ""
    log_info "數據目錄："
    echo "  - 用戶數據: ./data/users/"
    echo "  - 備份: ./data/backups/"
    echo "  - 日誌: ./data/logs/"
    
    echo ""
    log_info "管理指令："
    echo "  - 查看日誌: docker-compose logs -f"
    echo "  - 重啟服務: docker-compose restart"
    echo "  - 停止服務: docker-compose down"
}

# 備份數據
backup_data() {
    log_info "創建數據備份..."
    
    timestamp=$(date +%Y%m%d_%H%M%S)
    backup_dir="./backups_manual/backup_$timestamp"
    
    mkdir -p "$backup_dir"
    
    # 備份用戶數據
    if [[ -d "./data" ]]; then
        cp -r ./data "$backup_dir/"
        log_success "數據備份完成: $backup_dir"
    else
        log_warning "未找到數據目錄"
    fi
    
    # 備份配置文件
    cp .env "$backup_dir/" 2>/dev/null || log_warning "未找到 .env 文件"
    cp docker-compose.yml "$backup_dir/" 2>/dev/null || log_warning "未找到 docker-compose.yml"
    
    log_success "完整備份創建於: $backup_dir"
}

# 恢復數據
restore_data() {
    if [[ -z "$1" ]]; then
        log_error "請指定備份目錄路径"
        echo "用法: $0 restore /path/to/backup"
        exit 1
    fi
    
    backup_path="$1"
    
    if [[ ! -d "$backup_path" ]]; then
        log_error "備份目錄不存在: $backup_path"
        exit 1
    fi
    
    log_info "從備份恢復數據: $backup_path"
    
    # 停止服務
    docker-compose down
    
    # 恢復數據
    if [[ -d "$backup_path/data" ]]; then
        rm -rf ./data
        cp -r "$backup_path/data" ./
        log_success "數據恢復完成"
    else
        log_error "備份中未找到數據目錄"
        exit 1
    fi
    
    # 重啟服務
    docker-compose up -d
    log_success "服務重啟完成"
}

# 清理資源
cleanup() {
    log_info "清理 Docker 資源..."
    
    # 停止並移除容器
    docker-compose down
    
    # 移除映像（可選）
    read -p "是否要移除 Docker 映像? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker rmi linebot:latest 2>/dev/null || log_warning "映像移除失敗或不存在"
    fi
    
    # 清理未使用的資源
    docker system prune -f
    
    log_success "清理完成"
}

# 顯示日誌
show_logs() {
    local service="$1"
    
    if [[ -z "$service" ]]; then
        docker-compose logs -f
    else
        docker-compose logs -f "$service"
    fi
}

# 進入容器
enter_container() {
    local container_name="linebot-app"
    
    if docker ps | grep -q "$container_name"; then
        log_info "進入容器: $container_name"
        docker exec -it "$container_name" /bin/bash
    else
        log_error "容器未運行: $container_name"
    fi
}

# 更新應用
update_app() {
    log_info "更新應用..."
    
    # 備份當前數據
    backup_data
    
    # 重新構建映像
    build_image
    
    # 重新部署
    deploy_services
    
    # 等待服務啟動
    wait_for_services
    
    log_success "應用更新完成"
}

# 顯示幫助
show_help() {
    echo "LINE Bot Docker 部署腳本"
    echo ""
    echo "用法: $0 [COMMAND]"
    echo ""
    echo "指令:"
    echo "  deploy      - 完整部署（預設）"
    echo "  build       - 只構建 Docker 映像"
    echo "  start       - 啟動服務"
    echo "  stop        - 停止服務"
    echo "  restart     - 重啟服務"
    echo "  status      - 顯示服務狀態"
    echo "  logs [service] - 顯示日誌"
    echo "  backup      - 創建數據備份"
    echo "  restore <path> - 從備份恢復"
    echo "  cleanup     - 清理 Docker 資源"
    echo "  shell       - 進入容器"
    echo "  update      - 更新應用"
    echo "  health      - 檢查服務健康狀態"
    echo "  help        - 顯示此幫助"
    echo ""
    echo "範例:"
    echo "  $0 deploy           # 完整部署"
    echo "  $0 logs linebot     # 顯示 linebot 服務日誌"
    echo "  $0 backup           # 創建備份"
    echo "  $0 restore ./backups_manual/backup_20250604_120000  # 恢復備份"
}

# 檢查健康狀態
check_health() {
    log_info "檢查服務健康狀態..."
    
    # 檢查容器狀態
    if ! docker-compose ps | grep -q "Up"; then
        log_error "容器未運行"
        return 1
    fi
    
    # 檢查健康端點
    if curl -f http://localhost:8080/health &> /dev/null; then
        log_success "服務健康檢查通過"
        
        # 顯示詳細健康信息
        echo "健康檢查詳情:"
        curl -s http://localhost:8080/health | python3 -m json.tool 2>/dev/null || echo "無法解析健康檢查響應"
    else
        log_error "服務健康檢查失敗"
        return 1
    fi
    
    # 檢查數據目錄
    if [[ -d "./data" ]]; then
        log_info "數據目錄狀態:"
        echo "  - 用戶數據: $(ls -la ./data/users/ 2>/dev/null | wc -l) 個文件"
        echo "  - 備份: $(ls -la ./data/backups/ 2>/dev/null | wc -l) 個文件"
        echo "  - 日誌: $(ls -la ./data/logs/ 2>/dev/null | wc -l) 個文件"
    else
        log_warning "數據目錄不存在"
    fi
}

# 主執行邏輯
main() {
    local command="${1:-deploy}"
    
    case "$command" in
        "deploy")
            check_requirements
            setup_data_directories
            if setup_environment; then
                build_image
                deploy_services
                wait_for_services
                show_status
            else
                log_error "請先配置 .env 文件"
                exit 1
            fi
            ;;
        "build")
            check_requirements
            build_image
            ;;
        "start")
            docker-compose up -d
            wait_for_services
            show_status
            ;;
        "stop")
            docker-compose down
            log_success "服務已停止"
            ;;
        "restart")
            docker-compose restart
            wait_for_services
            log_success "服務已重啟"
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs "$2"
            ;;
        "backup")
            backup_data
            ;;
        "restore")
            restore_data "$2"
            ;;
        "cleanup")
            cleanup
            ;;
        "shell")
            enter_container
            ;;
        "update")
            update_app
            ;;
        "health")
            check_health
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            log_error "未知指令: $command"
            show_help
            exit 1
            ;;
    esac
}

# 執行主函數
main "$@"
