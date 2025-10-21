# TextDiff Docker 快速部署指南

## 🚀 一键部署

### 方式一：使用部署脚本（推荐）

```bash
# 运行自动部署脚本
./deploy.sh
```

脚本会引导您完成：
1. 环境变量配置
2. 选择部署模式（生产/开发）
3. 自动构建和启动服务

### 方式二：手动部署

#### 1. 配置环境变量

```bash
cp .env.example .env
vim .env  # 修改密码和密钥
```

#### 2. 生产环境部署

```bash
# 构建并启动
docker-compose up -d

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

访问: http://localhost

#### 3. 开发环境部署

```bash
# 启动开发环境（支持热重载）
docker-compose -f docker-compose.dev.yml up -d

# 查看日志
docker-compose -f docker-compose.dev.yml logs -f
```

访问: http://localhost:5173

## 📋 服务架构

```
┌─────────────────────────────────────┐
│         Nginx (端口 80)              │
│      反向代理 + 负载均衡              │
└──────────┬──────────────────────────┘
           │
    ┌──────┴───────┐
    │              │
┌───▼────┐    ┌───▼────┐
│Frontend│    │Backend │
│ (Vue3) │    │(FastAPI)│
│ Nginx  │    │ Uvicorn│
└────────┘    └───┬────┘
                  │
              ┌───▼────┐
              │ MySQL  │
              │  8.0   │
              └────────┘
```

## 📦 包含的服务

| 服务 | 容器名 | 端口 | 说明 |
|------|--------|------|------|
| Nginx | textdiff-nginx | 80, 443 | 反向代理 |
| Frontend | textdiff-frontend | 80 | Vue3前端 |
| Backend | textdiff-backend | 8000 | FastAPI后端 |
| MySQL | textdiff-db | 3306 | 数据库 |

## 🔧 常用命令

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f [service_name]

# 进入容器
docker-compose exec backend sh
docker-compose exec db mysql -u textdiff -p

# 重新构建
docker-compose build --no-cache

# 查看状态
docker-compose ps
```

## 💾 数据备份

```bash
# 备份数据库
docker-compose exec db mysqldump -u textdiff -p textdiff > backup.sql

# 恢复数据库
docker-compose exec -T db mysql -u textdiff -p textdiff < backup.sql
```

## 🐛 故障排查

### 端口冲突

修改 `.env` 文件中的端口配置：
```bash
NGINX_HTTP_PORT=8080
BACKEND_PORT=8001
```

### 查看详细日志

```bash
# 所有服务日志
docker-compose logs -f

# 特定服务日志
docker-compose logs -f backend
docker-compose logs -f db
```

### 重置所有数据

```bash
# ⚠️ 警告：这将删除所有数据！
docker-compose down -v
docker-compose up -d
```

## 🔒 安全提示

**生产环境部署前，请务必修改以下配置：**

1. `.env` 文件中的密码：
   - `MYSQL_ROOT_PASSWORD`
   - `MYSQL_PASSWORD`

2. JWT密钥（使用以下命令生成）：
   ```bash
   openssl rand -hex 32
   ```

3. 配置HTTPS证书（推荐使用Let's Encrypt）

## 📚 完整文档

详细部署文档请参考：[DOCKER_DEPLOY.md](./DOCKER_DEPLOY.md)

包含：
- 详细配置说明
- 性能优化建议
- 监控和日志管理
- HTTPS配置
- 滚动更新策略
- 完整故障排查指南

## 📞 需要帮助？

1. 查看完整文档: `DOCKER_DEPLOY.md`
2. 检查日志: `docker-compose logs -f`
3. 提交Issue到GitHub

---

**版本**: 1.0.0  
**最后更新**: 2024-10
