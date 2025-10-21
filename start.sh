#!/bin/bash

# TextDiff 启动脚本
# 用于同时启动后端和前端服务

echo "🚀 Starting TextDiff..."

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+"
    exit 1
fi

# 检查 Node.js 是否安装
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+"
    exit 1
fi

# 启动后端
echo "📦 Starting backend..."
cd backend

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
if [ ! -f ".deps_installed" ]; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
    touch .deps_installed
fi

# 检查环境配置
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
fi

# 后台启动后端
echo "Starting FastAPI server on http://localhost:8000"
python -m app.main &
BACKEND_PID=$!

cd ..

# 启动前端
echo "📦 Starting frontend..."
cd frontend

# 安装依赖
if [ ! -d "node_modules" ]; then
    echo "Installing Node dependencies..."
    npm install
fi

# 后台启动前端
echo "Starting Vite dev server on http://localhost:5173"
npm run dev &
FRONTEND_PID=$!

cd ..

# 等待服务启动
sleep 3

echo ""
echo "✅ TextDiff is running!"
echo ""
echo "📍 Frontend: http://localhost:5173"
echo "📍 Backend API: http://localhost:8000"
echo "📍 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# 等待用户中断
wait

# 清理进程
echo "Stopping services..."
kill $BACKEND_PID 2>/dev/null
kill $FRONTEND_PID 2>/dev/null

echo "👋 TextDiff stopped"
