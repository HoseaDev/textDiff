#!/bin/bash

# TextDiff 启动脚本 (Conda 版本)
# 用于同时启动后端和前端服务

echo "🚀 Starting TextDiff (Conda Environment)..."

# 检查 conda 是否安装
if ! command -v conda &> /dev/null; then
    echo "❌ Conda is not installed or not in PATH"
    echo "Please install Anaconda or Miniconda first"
    exit 1
fi

# 检查 Node.js 是否安装
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+"
    exit 1
fi

# 初始化 conda
eval "$(conda shell.bash hook)"

# 启动后端
echo "📦 Starting backend with Conda..."
cd backend

# 检查 conda 环境
CONDA_ENV_NAME="textdiff"

if ! conda env list | grep -q "^${CONDA_ENV_NAME} "; then
    echo "Creating conda environment: ${CONDA_ENV_NAME}..."
    conda create -n ${CONDA_ENV_NAME} python=3.11 -y
fi

# 激活 conda 环境
echo "Activating conda environment: ${CONDA_ENV_NAME}..."
conda activate ${CONDA_ENV_NAME}

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

# 返回项目根目录
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
echo "🔧 Conda Environment: ${CONDA_ENV_NAME}"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# 捕获中断信号
trap cleanup INT TERM

cleanup() {
    echo ""
    echo "Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "👋 TextDiff stopped"
    exit 0
}

# 等待用户中断
wait
