# 创建应用目录
sudo mkdir -p /var/www/tetris-battle
sudo chown -R $USER:$USER /var/www/tetris-battle

# 复制应用代码
cp -r . /var/www/tetris-battle/

# 安装依赖
cd /var/www/tetris-battle
npm install

# 配置环境变量
cat > .env << EOF
NODE_ENV=production
PORT=3000
DB_HOST=localhost
DB_USER=tetris_user
DB_PASSWORD=secure_password
DB_NAME=tetris_battle
JWT_SECRET=your_jwt_secret
REDIS_URL=redis://localhost:6379
EOF