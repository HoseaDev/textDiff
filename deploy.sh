#!/bin/bash

# TextDiff Docker部署脚本
set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  TextDiff Docker 部署脚本${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 检查Docker和Docker Compose
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: Docker未安装${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}错误: Docker Compose未安装${NC}"
    exit 1
fi

# 检查.env文件
if [ ! -f .env ]; then
    echo -e "${YELLOW}警告: .env文件不存在，正在创建...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}请编辑 .env 文件，修改数据库密码和密钥！${NC}"
    echo -e "${YELLOW}特别是以下配置：${NC}"
    echo "  - MYSQL_ROOT_PASSWORD"
    echo "  - MYSQL_PASSWORD"
    echo "  - SECRET_KEY"
    echo ""
    read -p "是否现在编辑.env文件？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ${EDITOR:-vim} .env
    else
        echo -e "${RED}请手动编辑.env文件后再运行此脚本！${NC}"
        exit 1
    fi
fi

# 部署模式选择
echo "请选择部署模式："
echo "1) 生产环境 (Production)"
echo "2) 开发环境 (Development)"
read -p "请输入选择 (1/2): " choice

case $choice in
    1)
        echo -e "${GREEN}正在部署生产环境...${NC}"
        COMPOSE_FILE="docker-compose.yml"
        ;;
    2)
        echo -e "${GREEN}正在部署开发环境...${NC}"
        COMPOSE_FILE="docker-compose.dev.yml"
        ;;
    *)
        echo -e "${RED}无效的选择${NC}"
        exit 1
        ;;
esac

# 构建镜像
echo ""
echo -e "${GREEN}步骤 1: 构建Docker镜像...${NC}"
docker-compose -f $COMPOSE_FILE build

# 启动服务
echo ""
echo -e "${GREEN}步骤 2: 启动服务...${NC}"
docker-compose -f $COMPOSE_FILE up -d

# 等待服务启动
echo ""
echo -e "${GREEN}步骤 3: 等待服务启动...${NC}"
sleep 5

# 检查服务状态
echo ""
echo -e "${GREEN}步骤 4: 检查服务状态...${NC}"
docker-compose -f $COMPOSE_FILE ps

# 显示访问信息
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  部署完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

if [ "$choice" = "1" ]; then
    echo "访问地址："
    echo "  - 前端: http://localhost"
    echo "  - 后端API: http://localhost/api"
    echo "  - WebSocket: ws://localhost/ws"
    echo ""
    echo "查看日志："
    echo "  docker-compose logs -f"
else
    echo "访问地址："
    echo "  - 前端: http://localhost:5173"
    echo "  - 后端API: http://localhost:8000"
    echo ""
    echo "查看日志："
    echo "  docker-compose -f docker-compose.dev.yml logs -f"
fi

echo ""
echo "停止服务："
echo "  docker-compose -f $COMPOSE_FILE down"
echo ""
echo -e "${YELLOW}提示: 首次运行可能需要初始化数据库${NC}"
echo -e "${YELLOW}请查看 DOCKER_DEPLOY.md 了解更多信息${NC}"
