# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装必要组件
sudo apt install -y nginx nodejs npm postgresql redis

# 配置防火墙
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable