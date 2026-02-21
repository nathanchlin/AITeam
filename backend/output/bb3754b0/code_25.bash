# 启用Nginx站点
sudo ln -s /etc/nginx/sites-available/flappybird /etc/nginx/sites-enabled/

# 测试Nginx配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx