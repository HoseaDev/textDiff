# Docker部署文件清单

## 📁 创建的文件列表

### 核心配置文件

1. **docker-compose.yml** - 生产环境Docker Compose配置
   - 包含MySQL数据库
   - FastAPI后端服务
   - Vue3前端服务
   - Nginx反向代理
   - 健康检查和数据持久化

2. **docker-compose.dev.yml** - 开发环境Docker Compose配置
   - 使用SQLite数据库
   - 支持热重载
   - 前端使用Vite开发服务器
   - 后端使用uvicorn --reload

3. **.env.example** - 环境变量模板
   - 数据库配置
   - JWT密钥配置
   - 端口配置
   - 应用基本配置

### Backend相关文件

4. **backend/Dockerfile** - 后端Docker镜像定义
   - 基于Python 3.11-slim
   - 安装MySQL客户端依赖
   - 配置Uvicorn服务器

5. **backend/.dockerignore** - 后端Docker构建忽略文件
   - 排除Python缓存、虚拟环境
   - 排除测试文件和日志

### Frontend相关文件

6. **frontend/Dockerfile** - 前端Docker镜像定义
   - 多阶段构建
   - 第一阶段：Node构建应用
   - 第二阶段：Nginx提供静态文件服务

7. **frontend/nginx.conf** - 前端Nginx配置
   - 支持Vue Router的history模式
   - 静态资源缓存配置
   - Gzip压缩
   - 安全头设置

8. **frontend/.dockerignore** - 前端Docker构建忽略文件
   - 排除node_modules
   - 排除构建产物

### Nginx相关文件

9. **nginx/nginx.conf** - 主Nginx反向代理配置
   - API请求转发到后端
   - WebSocket支持
   - 前端静态文件服务
   - CORS配置
   - 健康检查端点

### 部署脚本和文档

10. **deploy.sh** - 自动部署脚本
    - 交互式部署向导
    - 环境变量检查
    - 自动选择部署模式
    - 服务状态检查

11. **Makefile** - Make命令快捷方式
    - 简化的Docker命令
    - 数据备份/恢复
    - 开发/生产环境切换
    - 日志查看和清理

12. **DOCKER_DEPLOY.md** - 完整部署文档
    - 详细部署步骤
    - 故障排查指南
    - 性能优化建议
    - 安全配置说明
    - 监控和维护指南

13. **README_DOCKER.md** - Docker快速入门
    - 一键部署指南
    - 常用命令速查
    - 快速故障排查
    - 安全检查清单

### 其他文件

14. **.dockerignore** - 根目录Docker忽略文件
    - 通用的Docker构建忽略规则

15. **.gitignore** (更新)
    - 添加Docker相关忽略规则
    - 排除环境变量文件
    - 排除备份文件

## 🏗️ 文件结构

```
TextDiff/
├── docker-compose.yml              # 生产环境配置
├── docker-compose.dev.yml          # 开发环境配置
├── .env.example                    # 环境变量模板
├── .dockerignore                   # Docker忽略文件
├── deploy.sh                       # 自动部署脚本
├── Makefile                        # Make命令
├── DOCKER_DEPLOY.md               # 完整部署文档
├── README_DOCKER.md               # 快速入门
├── DOCKER_FILES_SUMMARY.md        # 本文件
│
├── backend/
│   ├── Dockerfile                 # 后端镜像
│   └── .dockerignore              # 后端忽略文件
│
├── frontend/
│   ├── Dockerfile                 # 前端镜像
│   ├── nginx.conf                 # 前端Nginx配置
│   └── .dockerignore              # 前端忽略文件
│
└── nginx/
    └── nginx.conf                 # 主Nginx配置
```

## 🚀 快速使用指南

### 方式1: 使用自动部署脚本（推荐新手）

```bash
./deploy.sh
```

### 方式2: 使用Make命令（推荐开发者）

```bash
# 查看所有命令
make help

# 生产环境
make build && make up

# 开发环境
make dev-build && make dev-up

# 查看日志
make logs
```

### 方式3: 使用Docker Compose命令（完全控制）

```bash
# 生产环境
docker-compose up -d

# 开发环境
docker-compose -f docker-compose.dev.yml up -d
```

## 📝 配置说明

### 必须修改的配置

在生产环境部署前，**必须**修改 `.env` 文件中的以下配置：

1. `MYSQL_ROOT_PASSWORD` - MySQL root密码
2. `MYSQL_PASSWORD` - 应用数据库密码
3. `SECRET_KEY` - JWT签名密钥（使用 `openssl rand -hex 32` 生成）

### 可选配置

- `NGINX_HTTP_PORT` - Nginx HTTP端口（默认80）
- `BACKEND_PORT` - 后端API端口（默认8000）
- `MYSQL_PORT` - MySQL端口（默认3306）

## 🔍 部署环境差异

| 特性 | 生产环境 | 开发环境 |
|------|---------|---------|
| 数据库 | MySQL 8.0 | SQLite |
| 前端 | Nginx静态文件 | Vite开发服务器 |
| 后端 | Uvicorn | Uvicorn --reload |
| 热重载 | ❌ | ✅ |
| 数据持久化 | ✅ | ✅ |
| 端口映射 | 80 | 5173, 8000 |

## 📊 服务端口

### 生产环境
- **80**: Nginx反向代理（对外访问）
- **8000**: 后端API（内部）
- **3306**: MySQL数据库（内部）

### 开发环境
- **5173**: 前端Vite开发服务器
- **8000**: 后端API
- 无数据库端口（使用SQLite文件）

## 🔧 维护命令

```bash
# 备份数据库
make backup

# 恢复数据库
make restore FILE=backups/backup_20241021_120000.sql

# 查看日志
make logs

# 重启服务
make restart

# 清理资源
make clean
```

## 📚 文档导航

- **快速开始**: 查看 `README_DOCKER.md`
- **完整部署**: 查看 `DOCKER_DEPLOY.md`
- **命令速查**: 运行 `make help`
- **问题排查**: 查看 `DOCKER_DEPLOY.md` 的故障排查章节

## ✅ 部署检查清单

部署前请确认：

- [ ] 已安装Docker和Docker Compose
- [ ] 已复制 `.env.example` 为 `.env`
- [ ] 已修改 `.env` 中的密码和密钥
- [ ] 已确认端口没有冲突
- [ ] 已阅读安全建议

部署后请检查：

- [ ] 所有容器正常运行（`docker-compose ps`）
- [ ] 前端可以访问
- [ ] 后端API可以访问
- [ ] 数据库连接正常
- [ ] 日志没有错误（`docker-compose logs`）

## 🆘 获取帮助

1. **查看日志**: `docker-compose logs -f`
2. **检查状态**: `docker-compose ps`
3. **参考文档**: `DOCKER_DEPLOY.md`
4. **提交Issue**: GitHub Issues

---

**版本**: 1.0.0  
**创建日期**: 2024-10  
**维护者**: TextDiff Team
