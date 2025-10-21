# 🚀 TextDiff Docker 快速启动

## 一分钟部署

```bash
# 1. 配置环境变量
cp .env.example .env

# 2. 编辑密钥（必须！）
vim .env
# 修改：MYSQL_ROOT_PASSWORD, MYSQL_PASSWORD, SECRET_KEY

# 3. 启动服务
./deploy.sh
# 选择: 1 (生产环境)

# 4. 访问应用
# http://localhost
```

## 命令速查表

### 部署命令

| 命令 | 说明 |
|------|------|
| `./deploy.sh` | 交互式部署 |
| `make up` | 启动生产环境 |
| `make dev-up` | 启动开发环境 |
| `make down` | 停止服务 |
| `make logs` | 查看日志 |
| `make ps` | 查看状态 |

### 直接使用Docker Compose

```bash
# 新版Docker (推荐)
docker compose up -d
docker compose ps
docker compose logs -f
docker compose down

# 旧版Docker
docker-compose up -d
docker-compose ps
docker-compose logs -f
docker-compose down
```

## 常见问题

### ❌ "docker-compose: command not found"

**解决**: 已修复！重新运行 `./deploy.sh` 即可

### ❌ "3306端口被占用"

**方案1**: 不映射MySQL端口（推荐）
```yaml
# 编辑 docker-compose.yml，注释掉：
# ports:
#   - "3306:3306"
```

**方案2**: 改用其他端口
```yaml
# 编辑 docker-compose.yml：
ports:
  - "3307:3306"  # 使用3307端口
```

### ❌ "80端口被占用"

```bash
# 编辑 docker-compose.yml：
nginx:
  ports:
    - "8080:80"  # 使用8080端口访问
```

## 服务地址

### 生产环境
- **前端**: http://localhost
- **API**: http://localhost/api
- **WebSocket**: ws://localhost/ws

### 开发环境
- **前端**: http://localhost:5173
- **后端**: http://localhost:8000

## 维护命令

```bash
# 备份数据库
make backup

# 查看日志
make logs

# 重启服务
make restart

# 完全清理（删除数据）
make clean-all
```

## 环境变量必改项

```bash
# .env 文件中必须修改：
MYSQL_ROOT_PASSWORD=强密码123
MYSQL_PASSWORD=强密码456
SECRET_KEY=$(openssl rand -hex 32)
```

## 验证部署

```bash
# 检查所有容器运行
docker compose ps

# 应该看到4个容器：
# - textdiff-nginx
# - textdiff-frontend
# - textdiff-backend
# - textdiff-db

# 测试访问
curl http://localhost/health
# 应返回: {"status":"healthy"}
```

## 获取帮助

```bash
# 查看所有Make命令
make help

# 查看部署文档
cat DOCKER_DEPLOY.md

# 查看修复说明
cat DOCKER_COMPOSE_FIX.md
```

## 问题排查

```bash
# 查看所有日志
docker compose logs

# 查看特定服务日志
docker compose logs backend
docker compose logs db

# 进入容器
docker compose exec backend sh
docker compose exec db mysql -u textdiff -p

# 重新构建
docker compose build --no-cache
docker compose up -d
```

---

**提示**: 首次部署可能需要5-10分钟下载镜像和构建，请耐心等待。
