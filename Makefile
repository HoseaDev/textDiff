.PHONY: help build up down restart logs ps clean backup restore

# 检测Docker Compose命令
COMPOSE := $(shell command -v docker-compose 2> /dev/null)
ifndef COMPOSE
	COMPOSE := docker compose
endif

# 默认目标
help:
	@echo "TextDiff Docker 管理命令"
	@echo ""
	@echo "生产环境命令:"
	@echo "  make build          - 构建所有镜像"
	@echo "  make up             - 启动所有服务"
	@echo "  make down           - 停止所有服务"
	@echo "  make restart        - 重启所有服务"
	@echo "  make logs           - 查看所有日志"
	@echo "  make ps             - 查看服务状态"
	@echo ""
	@echo "开发环境命令:"
	@echo "  make dev-build      - 构建开发环境镜像"
	@echo "  make dev-up         - 启动开发环境"
	@echo "  make dev-down       - 停止开发环境"
	@echo "  make dev-logs       - 查看开发环境日志"
	@echo ""
	@echo "维护命令:"
	@echo "  make clean          - 清理停止的容器和未使用的镜像"
	@echo "  make clean-all      - 清理所有数据（包括数据卷）"
	@echo "  make backup         - 备份数据库"
	@echo "  make restore        - 恢复数据库（需要指定 FILE=backup.sql）"
	@echo ""
	@echo "快速启动:"
	@echo "  ./deploy.sh         - 使用自动部署脚本"

# ========== 生产环境 ==========

build:
	@echo "构建生产环境镜像..."
	$(COMPOSE) build

up:
	@echo "启动生产环境..."
	$(COMPOSE) up -d
	@echo "服务已启动！访问 http://localhost"

down:
	@echo "停止生产环境..."
	$(COMPOSE) down

restart:
	@echo "重启生产环境..."
	$(COMPOSE) restart

logs:
	$(COMPOSE) logs -f

ps:
	$(COMPOSE) ps

# ========== 开发环境 ==========

dev-build:
	@echo "构建开发环境镜像..."
	$(COMPOSE) -f docker-compose.dev.yml build

dev-up:
	@echo "启动开发环境..."
	$(COMPOSE) -f docker-compose.dev.yml up -d
	@echo "服务已启动！"
	@echo "前端: http://localhost:5173"
	@echo "后端: http://localhost:8000"

dev-down:
	@echo "停止开发环境..."
	$(COMPOSE) -f docker-compose.dev.yml down

dev-logs:
	$(COMPOSE) -f docker-compose.dev.yml logs -f

# ========== 维护命令 ==========

clean:
	@echo "清理停止的容器和未使用的镜像..."
	$(COMPOSE) down
	docker system prune -f

clean-all:
	@echo "⚠️  警告: 这将删除所有数据！"
	@read -p "确认删除所有数据吗？(yes/no): " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		$(COMPOSE) down -v; \
		docker system prune -af --volumes; \
		echo "所有数据已清理！"; \
	else \
		echo "操作已取消"; \
	fi

backup:
	@echo "备份数据库..."
	@mkdir -p backups
	$(COMPOSE) exec -T db mysqldump -u textdiff -ptextdiff123 textdiff > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "备份完成！文件保存在 backups/ 目录"

restore:
	@if [ -z "$(FILE)" ]; then \
		echo "错误: 请指定备份文件，例如: make restore FILE=backup.sql"; \
		exit 1; \
	fi
	@echo "恢复数据库: $(FILE)"
	$(COMPOSE) exec -T db mysql -u textdiff -ptextdiff123 textdiff < $(FILE)
	@echo "数据库恢复完成！"

# ========== 快捷命令 ==========

shell-backend:
	@echo "进入后端容器..."
	$(COMPOSE) exec backend sh

shell-db:
	@echo "进入数据库容器..."
	$(COMPOSE) exec db mysql -u textdiff -p

rebuild:
	@echo "重新构建并启动..."
	make down
	make build
	make up

# ========== 测试命令 ==========

test:
	@echo "运行测试..."
	$(COMPOSE) exec backend pytest

test-cov:
	@echo "运行测试并生成覆盖率报告..."
	$(COMPOSE) exec backend pytest --cov=app
