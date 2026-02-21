# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装必要组件
sudo apt install nginx curl git -y

# 安装Node.js
curl -sL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt-get install -y nodejs

# 安装PM2
sudo npm install pm2 -g