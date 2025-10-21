# Docker Compose 兼容性修复

## 问题描述

在使用新版Docker时，可能会遇到以下错误：
```bash
./deploy.sh: line 72: docker-compose: command not found
```

## 原因

Docker已将Docker Compose从独立的`docker-compose`命令更新为Docker CLI插件`docker compose`（注意空格）：
- **旧版本**: `docker-compose` (带连字符)
- **新版本**: `docker compose` (带空格)

## 解决方案

已更新以下文件以自动兼容两种版本：

### 1. deploy.sh (部署脚本)
- 自动检测可用的命令格式
- 使用`$COMPOSE_CMD`变量存储正确的命令
- 运行时会显示使用的命令格式

### 2. Makefile
- 使用`$(COMPOSE)`变量自动检测命令
- 所有make命令现在都兼容两种格式

## 使用方法

### 现在可以正常使用：

```bash
# 方式1：使用部署脚本（推荐）
./deploy.sh

# 方式2：使用Make命令
make build && make up
make dev-build && make dev-up

# 方式3：直接使用Docker Compose
docker compose up -d           # 新版本
# 或
docker-compose up -d          # 旧版本（如果安装了）
```

## 验证修复

运行部署脚本时，会看到检测到的命令：

```bash
./deploy.sh
========================================
  TextDiff Docker 部署脚本
========================================

使用Docker Compose命令: docker compose    # <-- 显示检测结果
...
```

## 手动检查您的系统

```bash
# 检查是否有旧版docker-compose
which docker-compose

# 检查是否支持新版docker compose
docker compose version

# 检查Docker版本
docker --version
```

## 端口冲突提示

根据您的系统情况，MySQL 3306端口已被占用。有两个选择：

### 选项1：修改TextDiff使用的端口（推荐）

编辑 `.env` 文件：
```bash
MYSQL_PORT=3307  # 改为其他端口
```

然后修改 `docker-compose.yml` 中的端口映射：
```yaml
db:
  ports:
    - "3307:3306"  # 将外部端口改为3307
```

### 选项2：不映射MySQL端口到主机

如果只需要容器内部访问MySQL，可以删除端口映射：

编辑 `docker-compose.yml`：
```yaml
db:
  # ports:
  #   - "3306:3306"  # 注释掉这行
```

这样MySQL只能在Docker网络内部访问，更安全。

## 快速部署步骤

```bash
# 1. 配置环境变量
cp .env.example .env
vim .env  # 修改密码和密钥

# 2. （可选）处理端口冲突
# 如果3306端口被占用，按上面的方法修改

# 3. 运行部署
./deploy.sh

# 4. 选择生产环境(1)

# 5. 查看服务状态
docker compose ps
# 或
docker-compose ps
```

## 常见问题

### Q: 如何确定使用哪个命令？

A: 脚本会自动检测，您不需要关心。如果想手动查看：
```bash
command -v docker-compose && echo "旧版本可用" || echo "旧版本不可用"
docker compose version 2>/dev/null && echo "新版本可用" || echo "新版本不可用"
```

### Q: 可以同时安装两个版本吗？

A: 可以。如果同时存在，脚本会优先使用旧版本的`docker-compose`命令。

### Q: 需要重新安装吗？

A: 不需要。只需要拉取更新的代码文件即可。

## 更新记录

- **2024-10-21**: 修复Docker Compose命令兼容性问题
  - 更新 `deploy.sh` 支持自动检测
  - 更新 `Makefile` 支持自动检测
  - 所有命令现在都兼容新旧版本

## 相关文档

- [完整部署文档](./DOCKER_DEPLOY.md)
- [快速入门](./README_DOCKER.md)
- [文件清单](./DOCKER_FILES_SUMMARY.md)
