# TextDiff - Conda 环境启动指南

本文档专门为使用 Conda 环境的用户提供启动说明。

## 方法一：使用自动脚本（推荐）

### 一键启动
```bash
cd /Users/harry/PycharmProjects/TextDiff
./start-conda.sh
```

脚本会自动：
1. 创建名为 `textdiff` 的 conda 环境（如果不存在）
2. 安装所有 Python 依赖
3. 启动后端服务（端口 8000）
4. 安装前端依赖
5. 启动前端服务（端口 5173）

### 停止服务
按 `Ctrl+C` 停止所有服务

---

## 方法二：手动启动（完全控制）

### 步骤 1: 创建和配置 Conda 环境

```bash
# 创建 conda 环境
conda create -n textdiff python=3.11 -y

# 激活环境
conda activate textdiff

# 进入后端目录
cd backend

# 安装 Python 依赖
pip install -r requirements.txt

# 创建环境配置文件
cp .env.example .env
```

### 步骤 2: 启动后端

```bash
# 确保在 backend 目录并且 conda 环境已激活
conda activate textdiff
cd backend

# 启动后端服务
python -m app.main
```

后端将在 `http://localhost:8000` 运行

### 步骤 3: 启动前端（新终端）

```bash
# 打开新终端窗口
cd /Users/harry/PycharmProjects/TextDiff/frontend

# 安装依赖（首次运行）
npm install

# 启动开发服务器
npm run dev
```

前端将在 `http://localhost:5173` 运行

---

## 方法三：使用现有 Conda 环境

如果您已经有一个 conda 环境想要使用：

```bash
# 激活您的现有环境
conda activate 您的环境名

# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 启动后端
python -m app.main
```

然后在另一个终端启动前端（步骤 3）。

---

## 验证安装

### 检查后端
```bash
# 访问健康检查端点
curl http://localhost:8000/health

# 应该返回：{"status":"healthy"}
```

### 检查前端
浏览器访问：http://localhost:5173

---

## 常见问题

### Q1: conda 命令未找到
**解决方案：**
```bash
# 初始化 conda（根据您的 shell）
# Bash
echo '. ~/anaconda3/etc/profile.d/conda.sh' >> ~/.bashrc
source ~/.bashrc

# Zsh
echo '. ~/anaconda3/etc/profile.d/conda.sh' >> ~/.zshrc
source ~/.zshrc
```

### Q2: conda activate 不工作
**解决方案：**
```bash
# 初始化 conda shell
conda init bash  # 或 conda init zsh

# 重新打开终端，然后再试
conda activate textdiff
```

### Q3: 端口已被占用
**解决方案：**
```bash
# 查找占用端口的进程
lsof -i :8000  # 后端
lsof -i :5173  # 前端

# 杀死进程
kill -9 <PID>

# 或者在脚本中使用不同端口
```

### Q4: 依赖安装失败
**解决方案：**
```bash
# 清除缓存重新安装
conda activate textdiff
pip cache purge
pip install -r requirements.txt --no-cache-dir
```

### Q5: 想要删除环境重新开始
```bash
# 停用环境
conda deactivate

# 删除环境
conda env remove -n textdiff

# 重新创建
conda create -n textdiff python=3.11 -y
conda activate textdiff
cd backend
pip install -r requirements.txt
```

---

## 开发建议

### 在 IDE 中使用 Conda 环境

#### VS Code
1. 打开命令面板 (`Cmd+Shift+P`)
2. 选择 `Python: Select Interpreter`
3. 选择 `textdiff` conda 环境

#### PyCharm
1. 打开设置 (`Cmd+,`)
2. Project > Python Interpreter
3. Add Interpreter > Conda Environment
4. 选择 `textdiff` 环境

### 添加新的 Python 包
```bash
conda activate textdiff
pip install 包名

# 更新 requirements.txt
pip freeze > requirements.txt
```

### 环境导出（方便团队共享）
```bash
# 导出 conda 环境配置
conda activate textdiff
conda env export > environment.yml

# 其他人可以用这个文件创建相同环境
# conda env create -f environment.yml
```

---

## 性能优化建议

### 使用 conda-forge 加速安装
```bash
conda config --add channels conda-forge
conda config --set channel_priority strict
```

### 使用 mamba（更快的包管理器）
```bash
# 安装 mamba
conda install mamba -n base -c conda-forge

# 使用 mamba 创建环境（更快）
mamba create -n textdiff python=3.11 -y
```

---

## 生产部署

对于生产环境，建议：

1. **使用固定版本的依赖**
```bash
pip freeze > requirements-lock.txt
```

2. **使用 conda 打包**
```bash
conda pack -n textdiff -o textdiff.tar.gz
```

3. **使用 Docker**（推荐）
```dockerfile
FROM continuumio/miniconda3
COPY environment.yml .
RUN conda env create -f environment.yml
...
```

---

## 下一步

- 查看 [README.md](README.md) 了解完整功能
- 查看 [QUICKSTART.md](QUICKSTART.md) 了解快速使用
- 访问 http://localhost:8000/docs 查看 API 文档

开始使用 TextDiff！🚀
