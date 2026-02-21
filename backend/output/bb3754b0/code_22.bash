# 创建网站目录
sudo mkdir -p /var/www/flappybird
sudo chown -R $USER:$USER /var/www/flappybird

# 设置Nginx配置
sudo nano /etc/nginx/sites-available/flappybird