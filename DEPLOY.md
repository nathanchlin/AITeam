# 腾讯云部署指南

## 服务器要求

- **推荐配置**: 腾讯云轻量应用服务器
- **CPU/内存**: 2核 4GB 起
- **系统**: Ubuntu 20.04 或 22.04
- **带宽**: 3Mbps 起

## 快速部署

### 1. 连接服务器

```bash
ssh root@your-server-ip
```

### 2. 安装 Docker

```bash
curl -fsSL https://get.docker.com | bash
systemctl enable docker && systemctl start docker

# 安装 Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

### 3. 克隆项目

```bash
git clone https://github.com/nathanchlin/AITeam.git
cd AITeam
```

### 4. 配置环境变量

```bash
# 创建后端环境配置
cat > backend/.env << EOF
GLM_API_KEY=your_glm_api_key_here
GLM_MODEL=glm-5
DEBUG=false
CORS_ORIGINS=*
EOF
```

### 5. 一键部署

```bash
chmod +x deploy.sh
./deploy.sh deploy
```

部署完成后访问 `http://your-server-ip`

## 常用命令

```bash
# 查看日志
./deploy.sh logs

# 更新代码
./deploy.sh update

# 重启服务
./deploy.sh restart

# 停止服务
./deploy.sh stop
```

## 配置 HTTPS (可选)

### 方法一: 使用 Let's Encrypt

```bash
# 需要先解析域名到服务器 IP
./deploy.sh ssl your-domain.com
```

然后编辑 `nginx.conf`，取消 SSL 相关配置的注释，最后重启:

```bash
./deploy.sh restart
```

### 方法二: 使用腾讯云 SSL 证书

1. 在腾讯云控制台申请免费 SSL 证书
2. 下载 Nginx 格式证书
3. 上传到服务器的 `ssl/` 目录:
   ```bash
   # 重命名为以下文件名
   ssl/fullchain.pem  # 证书文件
   ssl/privkey.pem    # 私钥文件
   ```
4. 修改 `nginx.conf` 启用 SSL
5. 重启服务

## 修改 nginx.conf 启用 SSL

找到以下内容并取消注释:

```nginx
# 将这行
listen 80;

# 改为
listen 443 ssl http2;

# 并取消以下注释
ssl_certificate /etc/nginx/ssl/fullchain.pem;
ssl_certificate_key /etc/nginx/ssl/ssl/privkey.pem;
```

同时取消 HTTP 重定向的注释:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

## 防火墙配置

确保以下端口开放:

```bash
# 腾讯云控制台 - 安全组规则
# 入站规则:
# - 80 (HTTP)
# - 443 (HTTPS)
# - 22 (SSH)

# 或使用 ufw
ufw allow 80
ufw allow 443
ufw allow 22
ufw enable
```

## 故障排查

### 查看容器状态
```bash
docker-compose -f docker-compose.prod.yml ps
```

### 查看详细日志
```bash
# 所有服务
docker-compose -f docker-compose.prod.yml logs

# 特定服务
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml logs frontend
docker-compose -f docker-compose.prod.yml logs nginx
```

### 进入容器调试
```bash
docker-compose -f docker-compose.prod.yml exec backend bash
```

### 重置部署
```bash
./deploy.sh stop
docker-compose -f docker-compose.prod.yml down -v
./deploy.sh deploy
```

## 数据备份

数据存储在 `./data` 目录，定期备份:

```bash
# 备份
tar -czvf aiteam-backup-$(date +%Y%m%d).tar.gz data/

# 恢复
tar -xzvf aiteam-backup-20240301.tar.gz
```

## 性能优化建议

1. **启用 CDN**: 将前端静态资源放到腾讯云 CDN
2. **数据库升级**: 生产环境建议使用腾讯云数据库替代 JSON 文件
3. **负载均衡**: 高并发场景可配置多个后端实例
