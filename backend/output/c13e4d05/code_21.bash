#!/bin/bash
# 部署脚本

# 更新代码
git pull origin main

# 安装依赖
npm install

# 构建项目 (如果有构建步骤)
npm run build

# 重启Web服务器
sudo systemctl reload nginx

# 验证部署
curl -I https://yourdomain.com