# 初始化Git仓库
git init

# 创建.gitignore文件
echo "*.pyc" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "venv/" >> .gitignore
echo ".env" >> .gitignore

# 添加初始文件
git add .
git commit -m "Initial commit: Tetris game project"