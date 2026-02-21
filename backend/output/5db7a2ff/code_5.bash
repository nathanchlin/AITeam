# 安装Git（根据您的操作系统）
# Windows: 下载并安装Git for Windows
# macOS: 使用Homebrew: brew install git
# Linux: 使用包管理器，如sudo apt-get install git

# 初始化Git仓库
git init

# 配置用户信息
git config --global user.name "您的姓名"
git config --global user.email "您的邮箱"

# 创建.gitignore文件（防止不必要的文件被提交）
echo "node_modules/" >> .gitignore
echo "dist/" >> .gitignore
echo "*.log" >> .gitignore