# 初始化PostgreSQL
sudo -u postgres createdb tetris_battle
sudo -u postgres psql -c "CREATE USER tetris_user WITH PASSWORD 'secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE tetris_battle TO tetris_user;"

# 导入数据库结构
psql -h localhost -U tetris_user -d tetris_battle -f schema.sql