#!/bin/bash

# TextDiff Conda 环境设置脚本
# 仅用于创建和配置 conda 环境

echo "🔧 Setting up TextDiff Conda Environment..."

# 检查 conda 是否安装
if ! command -v conda &> /dev/null; then
    echo "❌ Conda is not installed or not in PATH"
    echo "Please install Anaconda or Miniconda from:"
    echo "https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

# 初始化 conda
eval "$(conda shell.bash hook)"

CONDA_ENV_NAME="textdiff"

# 检查环境是否已存在
if conda env list | grep -q "^${CONDA_ENV_NAME} "; then
    echo "⚠️  Conda environment '${CONDA_ENV_NAME}' already exists."
    read -p "Do you want to remove and recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing existing environment..."
        conda env remove -n ${CONDA_ENV_NAME} -y
    else
        echo "Using existing environment."
        conda activate ${CONDA_ENV_NAME}
        cd backend
        echo "Updating dependencies..."
        pip install -r requirements.txt
        cd ..
        echo "✅ Environment updated!"
        exit 0
    fi
fi

# 创建新环境
echo "Creating conda environment: ${CONDA_ENV_NAME}..."
conda create -n ${CONDA_ENV_NAME} python=3.11 -y

if [ $? -ne 0 ]; then
    echo "❌ Failed to create conda environment"
    exit 1
fi

# 激活环境
echo "Activating conda environment..."
conda activate ${CONDA_ENV_NAME}

# 安装后端依赖
echo "Installing Python dependencies..."
cd backend

if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found in backend/"
    exit 1
fi

pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install Python dependencies"
    exit 1
fi

# 创建环境配置文件
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "✅ .env file created (you can modify it later)"
else
    echo "ℹ️  .env file already exists"
fi

cd ..

# 安装前端依赖
echo "Installing Node.js dependencies..."
cd frontend

if ! command -v node &> /dev/null; then
    echo "⚠️  Node.js is not installed. Please install Node.js 18+ to use the frontend."
    echo "You can download it from: https://nodejs.org/"
else
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install Node dependencies"
        exit 1
    fi
    echo "✅ Frontend dependencies installed"
fi

cd ..

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo ""
echo "1. To activate the environment:"
echo "   conda activate ${CONDA_ENV_NAME}"
echo ""
echo "2. To start the application:"
echo "   ./start-conda.sh"
echo ""
echo "   Or manually:"
echo "   Terminal 1: conda activate ${CONDA_ENV_NAME} && cd backend && python -m app.main"
echo "   Terminal 2: cd frontend && npm run dev"
echo ""
echo "3. Access the application:"
echo "   Frontend: http://localhost:5173"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📚 For more information, see CONDA_SETUP.md"
echo ""
