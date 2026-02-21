# 安装Certbot
sudo apt install certbot python3-certbot-nginx -y

# 获取SSL证书
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# 自动续期设置
sudo crontab -e
# 添加以下行：
0 12 * * * /usr/bin/certbot renew --quiet