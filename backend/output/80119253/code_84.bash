#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/$USER/backups"
mkdir -p $BACKUP_DIR

# 备份代码
tar -czf $BACKUP_DIR/gomoku_$DATE.tar.gz /var/www/gomoku

# 保留最近7天的备份
find $BACKUP_DIR -name "gomoku_*.tar.gz" -mtime +7 -delete