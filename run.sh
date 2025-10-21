#!/bin/bash

# 简单启动脚本 - Conda 版本

echo "🚀 启动 TextDiff..."

# 后端
cd backend
conda activate textdiff 2>/dev/null || conda create -n textdiff python=3.11 -y && conda activate textdiff
pip install -r requirements.txt -q
cp .env.example .env 2>/dev/null
python -m app.main &
BACKEND_PID=$!

cd ../frontend
npm install -q
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ 服务已启动"
echo "前端: http://localhost:5173"
echo "后端: http://localhost:8000"
echo ""
echo "按 Ctrl+C 停止"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM

wait
