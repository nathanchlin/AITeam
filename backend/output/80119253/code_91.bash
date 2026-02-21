# 拉取最新代码
cd /var/www/gomoku
git pull origin main

# 重新构建（如果需要）
npm run build

# 重启服务（如果需要）
sudo systemctl restart nginx
pm2 reload gomoku-backend