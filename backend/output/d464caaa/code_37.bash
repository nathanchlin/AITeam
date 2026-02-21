# 初始化Git仓库
git init

# 添加.gitignore文件
echo "node_modules/
dist/
build/
*.log
.env
.DS_Store" > .gitignore

# 创建初始提交
git add .
git commit -m "Initial commit: Russian方块对战游戏项目"