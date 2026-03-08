#!/bin/bash

# AITeam 腾讯云部署脚本
# 使用方法: ./deploy.sh [命令]
# 命令: deploy | update | logs | stop | restart | ssl

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 检查 Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose 未安装"
        exit 1
    fi
}

# 检查环境变量
check_env() {
    if [ ! -f backend/.env ]; then
        log_warn "backend/.env 文件不存在，正在创建..."
        cp backend/.env.example backend/.env 2>/dev/null || echo "GLM_API_KEY=your_api_key_here" > backend/.env
        log_warn "请编辑 backend/.env 填入你的 GLM_API_KEY"
        exit 1
    fi

    if grep -q "your_api_key_here" backend/.env 2>/dev/null; then
        log_error "请在 backend/.env 中设置正确的 GLM_API_KEY"
        exit 1
    fi
}

# 部署
deploy() {
    log_info "开始部署 AITeam..."
    check_docker
    check_env

    # 创建数据目录
    mkdir -p data ssl

    # 构建并启动
    log_info "构建 Docker 镜像..."
    docker compose -f docker-compose.prod.yml build

    log_info "启动服务..."
    docker compose -f docker-compose.prod.yml up -d

    log_info "等待服务启动..."
    sleep 5

    # 检查状态
    if docker compose -f docker-compose.prod.yml ps | grep -q "Up"; then
        log_info "部署成功！"
        log_info "访问地址: http://$(curl -s ifconfig.me 2>/dev/null || echo 'your-server-ip')"
    else
        log_error "部署失败，请检查日志: ./deploy.sh logs"
    fi
}

# 更新
update() {
    log_info "更新 AITeam..."
    check_docker

    log_info "拉取最新代码..."
    git pull

    log_info "重新构建并启动..."
    docker compose -f docker-compose.prod.yml build --no-cache
    docker compose -f docker-compose.prod.yml up -d

    log_info "清理旧镜像..."
    docker image prune -f

    log_info "更新完成！"
}

# 查看日志
logs() {
    docker compose -f docker-compose.prod.yml logs -f --tail=100
}

# 停止
stop() {
    log_info "停止服务..."
    docker compose -f docker-compose.prod.yml down
    log_info "服务已停止"
}

# 重启
restart() {
    log_info "重启服务..."
    docker compose -f docker-compose.prod.yml restart
    log_info "服务已重启"
}

# SSL 证书 (使用 Let's Encrypt)
ssl() {
    log_info "配置 SSL 证书..."

    if [ -z "$1" ]; then
        log_error "请提供域名: ./deploy.sh ssl your-domain.com"
        exit 1
    fi

    DOMAIN=$1

    # 安装 certbot
    if ! command -v certbot &> /dev/null; then
        log_info "安装 certbot..."
        apt-get update && apt-get install -y certbot
    fi

    # 获取证书
    log_info "获取 SSL 证书..."
    certbot certonly --standalone -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN

    # 复制证书
    cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem ssl/
    cp /etc/letsencrypt/live/$DOMAIN/privkey.pem ssl/

    log_info "SSL 证书已配置"
    log_warn "请修改 nginx.conf 启用 SSL，然后运行 ./deploy.sh restart"
}

# 主命令
case "$1" in
    deploy|"")
        deploy
        ;;
    update)
        update
        ;;
    logs)
        logs
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    ssl)
        ssl "$2"
        ;;
    *)
        echo "使用方法: $0 {deploy|update|logs|stop|restart|ssl <domain>}"
        exit 1
        ;;
esac
