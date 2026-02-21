# 启用站点
sudo ln -s /etc/nginx/sites-available/gomoku /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx