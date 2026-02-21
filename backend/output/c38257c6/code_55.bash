#!/bin/bash
# deploy.sh

# 设置变量
REMOTE_USER="deploy"
REMOTE_HOST="yourserver.com"
REMOTE_DIR="/var/www/game"
LOCAL_BUILD_DIR="dist"

# 构建项目
npm run build

# 备份当前版本
ssh ${REMOTE_USER}@${REMOTE_HOST} "cp -r ${REMOTE_DIR} ${REMOTE_DIR}.backup.$(date +%Y%m%d%H%M%S)"

# 上传新版本
rsync -avz --delete ${LOCAL_BUILD_DIR}/ ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}

# 设置权限
ssh ${REMOTE_USER}@${REMOTE_HOST} "chown -R www-data:www-data ${REMOTE_DIR}"

# 重启服务（如果需要）
ssh ${REMOTE_USER}@${REMOTE_HOST} "systemctl reload nginx"