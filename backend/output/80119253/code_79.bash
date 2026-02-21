# 创建后端目录
sudo mkdir -p /var/www/gomoku-backend
sudo chown -R $USER:$USER /var/www/gomoku-backend

# 上传后端代码
cd /var/www/gomoku-backend
git clone https://github.com/yourusername/gomoku-backend.git .

# 安装依赖
npm install

# 使用PM2启动服务
pm2 start app.js --name "gomoku-backend"