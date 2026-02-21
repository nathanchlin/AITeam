# 安装必要组件
sudo apt update
sudo apt install -y docker.io docker-compose kubectl nginx

# 配置防火墙
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable