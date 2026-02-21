# 创建网站目录
sudo mkdir -p /var/www/gomoku
sudo chown -R $USER:$USER /var/www/gomoku

# 上传构建后的文件
# 可以使用git clone或直接上传文件
cd /var/www/gomoku
git clone https://github.com/yourusername/gomoku-game.git .

# 如果是纯静态文件，直接上传到该目录