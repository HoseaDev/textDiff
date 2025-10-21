# TextDiff Docker 部署文档

## 📦 项目架构

```
TextDiff
├── backend/              # FastAPI后端服务
│   ├── Dockerfile
│   └── .dockerignore
├── frontend/             # Vue 3前端服务
│   ├── Dockerfile
│   ├── nginx.conf       # 前端Nginx配置
│   └── .dockerignore
├── nginx/               # 主Nginx反向代理
│   └── nginx.conf
├── docker-compose.yml   # 生产环境配置
├── docker-compose.dev.yml  # 开发环境配置
└── .env.example         # 环境变量示例
```

## 🚀 快速开始

### 前置要求

- Docker 20.10+
- Docker Compose 2.0+

### 1. 克隆项目并配置环境变量

```bash
# 复制环境变量文件
cp .env.example .env

# 编辑.env文件，修改关键配置（特别是密码和密钥）
vim .env
```

**⚠️ 重要：生产环境必须修改以下配置：**
- `MYSQL_ROOT_PASSWORD`
- `MYSQL_PASSWORD`
- `SECRET_KEY` (使用 `openssl rand -hex 32` 生成)

### 2. 部署生产环境

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

访问应用：
- **前端**: http://localhost
- **后端API**: http://localhost/api
- **WebSocket**: ws://localhost/ws

### 3. 开发环境部署

开发环境使用热重载，修改代码后自动刷新。

```bash
# 启动开发环境
docker-compose -f docker-compose.dev.yml up -d

# 查看日志
docker-compose -f docker-compose.dev.yml logs -f
```

访问应用：
- **前端开发服务器**: http://localhost:5173
- **后端API**: http://localhost:8000

## 📋 常用命令

### 服务管理

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 停止并删除数据卷（谨慎使用！）
docker-compose down -v

# 重启特定服务
docker-compose restart backend
docker-compose restart frontend
docker-compose restart nginx

# 查看服务状态
docker-compose ps

# 查看服务日志
docker-compose logs -f [service_name]
```

### 镜像管理

```bash
# 重新构建镜像
docker-compose build

# 重新构建特定服务
docker-compose build backend
docker-compose build frontend

# 不使用缓存重新构建
docker-compose build --no-cache

# 拉取最新基础镜像
docker-compose pull
```

### 容器操作

```bash
# 进入后端容器
docker-compose exec backend sh

# 进入数据库容器
docker-compose exec db mysql -u textdiff -p

# 查看后端日志
docker-compose logs -f backend

# 查看Nginx日志
docker-compose logs -f nginx
```

## 🗄️ 数据库管理

### 初始化数据库

```bash
# 进入后端容器
docker-compose exec backend sh

# 运行数据库迁移
cd /app
alembic upgrade head
```

### 备份数据库

```bash
# 备份MySQL数据
docker-compose exec db mysqldump -u textdiff -p textdiff > backup_$(date +%Y%m%d_%H%M%S).sql

# 导出数据卷
docker run --rm \
  -v textdiff_mysql_data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/mysql_backup_$(date +%Y%m%d_%H%M%S).tar.gz -C /data .
```

### 恢复数据库

```bash
# 从SQL文件恢复
docker-compose exec -T db mysql -u textdiff -p textdiff < backup.sql

# 从数据卷备份恢复
docker run --rm \
  -v textdiff_mysql_data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/mysql_backup.tar.gz -C /data
```

## 🔧 故障排查

### 1. 端口冲突

如果默认端口被占用：

```bash
# 修改.env文件中的端口配置
NGINX_HTTP_PORT=8080
BACKEND_PORT=8001
MYSQL_PORT=3307
```

然后修改 `docker-compose.yml` 中对应的端口映射。

### 2. 数据库连接失败

```bash
# 检查数据库健康状态
docker-compose ps db

# 查看数据库日志
docker-compose logs db

# 确保数据库完全启动后再启动后端
docker-compose up -d db
# 等待10秒
docker-compose up -d backend
```

### 3. 前端无法访问后端API

检查Nginx配置和网络：

```bash
# 测试后端服务
docker-compose exec nginx wget -O- http://backend:8000/health

# 检查网络连接
docker network inspect textdiff_textdiff-network
```

### 4. 查看详细错误日志

```bash
# 后端错误日志
docker-compose logs --tail=100 backend

# Nginx错误日志
docker-compose exec nginx cat /var/log/nginx/error.log

# 数据库错误日志
docker-compose logs db
```

### 5. 容器无法启动

```bash
# 查看容器启动日志
docker-compose up

# 强制重建
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 🔒 安全建议

### 生产环境安全清单

- [ ] 修改所有默认密码
- [ ] 使用强随机密钥（`openssl rand -hex 32`）
- [ ] 配置HTTPS（使用Let's Encrypt）
- [ ] 限制数据库端口仅内网访问
- [ ] 定期备份数据
- [ ] 配置防火墙规则
- [ ] 启用日志监控
- [ ] 定期更新依赖和镜像

### 配置HTTPS（使用Let's Encrypt）

1. 安装Certbot:
```bash
docker-compose exec nginx apk add certbot certbot-nginx
```

2. 获取SSL证书:
```bash
docker-compose exec nginx certbot --nginx -d yourdomain.com
```

3. 修改nginx配置支持HTTPS（参考nginx/nginx.conf）

## 📊 性能优化

### 1. 数据库优化

在 `docker-compose.yml` 中添加MySQL性能配置：

```yaml
db:
  command: 
    - --innodb-buffer-pool-size=512M
    - --max-connections=200
```

### 2. 后端并发优化

修改后端启动命令：

```yaml
backend:
  command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 3. Nginx缓存

在 `nginx/nginx.conf` 中添加缓存配置。

## 🔄 更新部署

### 更新代码

```bash
# 拉取最新代码
git pull

# 重新构建并重启
docker-compose down
docker-compose build
docker-compose up -d
```

### 滚动更新（零停机）

```bash
# 更新后端（不停机）
docker-compose build backend
docker-compose up -d --no-deps --scale backend=2 backend
docker-compose up -d --no-deps --scale backend=1 backend

# 更新前端（不停机）
docker-compose build frontend
docker-compose up -d --no-deps frontend
```

## 📈 监控

### 健康检查端点

- Nginx健康检查: http://localhost/health
- 后端健康检查: http://localhost/api/health

### 查看资源使用

```bash
# 查看容器资源使用
docker stats

# 查看数据卷大小
docker system df -v
```

## 🧪 测试部署

```bash
# 测试后端API
curl http://localhost/api/health

# 测试前端
curl http://localhost

# 测试WebSocket
wscat -c ws://localhost/ws/document/test-id
```

## 📞 技术支持

如遇到问题：

1. 查看日志: `docker-compose logs -f`
2. 检查服务状态: `docker-compose ps`
3. 参考故障排查章节
4. 提交Issue到GitHub

## 📝 版本说明

- Docker版本: 20.10+
- Docker Compose版本: 2.0+
- Python版本: 3.11
- Node版本: 20
- MySQL版本: 8.0
- Nginx版本: Alpine

---

**最后更新**: 2024-10
**维护者**: TextDiff Team
