# TextDiff 快速启动指南

## 一键启动（推荐）

### macOS / Linux
```bash
./start.sh
```

### Windows
```bash
# 1. 启动后端（终端1）
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m app.main

# 2. 启动前端（终端2）
cd frontend
npm install
npm run dev
```

## 手动启动

### 步骤 1: 后端设置

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt

# 复制环境配置
cp .env.example .env

# 启动后端
python -m app.main
```

后端将在 `http://localhost:8000` 运行

### 步骤 2: 前端设置

```bash
# 打开新终端，进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将在 `http://localhost:5173` 运行

## 访问应用

打开浏览器访问：
- 🌐 应用主页：http://localhost:5173
- 📚 API 文档：http://localhost:8000/docs
- 🔍 健康检查：http://localhost:8000/health

## 首次使用

1. 访问 http://localhost:5173
2. 开始输入文本
3. 点击"保存"按钮或按 Ctrl+S
4. 查看左侧版本历史
5. 尝试修改文本后再次保存
6. 点击"查看差异"查看版本对比

## 常用功能

### 保存文档
- **快捷键**：`Ctrl+S` (Windows) / `Cmd+S` (Mac)
- **按钮**：点击工具栏的"保存"按钮
- **自动保存**：在设置中启用（默认30秒）

### 版本对比
1. 点击"查看差异"按钮
2. 选择对比模式（智能、行级、单词、字符）
3. 查看高亮的变化

### 版本恢复
1. 在左侧版本列表选择历史版本
2. 点击该版本查看内容
3. 如需恢复，系统会创建新版本

### 移动端访问
在手机或平板浏览器访问：
- 确保设备与电脑在同一网络
- 访问 `http://你的电脑IP:5173`

## 配置说明

### 保存设置
点击右上角"设置"按钮：
- **保存模式**：选择手动/自动/混合
- **自动保存间隔**：5-300秒可调
- **确认选项**：保存前确认、离开警告等

### 高级配置

#### 后端配置 (backend/.env)
```bash
DATABASE_URL=sqlite:///./textdiff.db
SECRET_KEY=your-secret-key
ALLOWED_ORIGINS=["http://localhost:5173"]
```

#### 切换到 PostgreSQL
```bash
# 在 backend/.env 中修改
DATABASE_URL=postgresql://user:password@localhost:5432/textdiff

# 安装 PostgreSQL 驱动
pip install psycopg2-binary
```

## 故障排除

### 后端无法启动
```bash
# 检查 Python 版本
python3 --version  # 需要 3.11+

# 重新安装依赖
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 前端无法启动
```bash
# 检查 Node 版本
node --version  # 需要 18+

# 清除缓存重装
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### 端口已被占用
```bash
# 查找占用端口的进程
lsof -i :8000  # 后端
lsof -i :5173  # 前端

# 杀死进程
kill -9 <PID>
```

### 数据库问题
```bash
# 删除数据库重新初始化
cd backend
rm textdiff.db
python -m app.main  # 会自动创建新数据库
```

## 停止服务

### 使用 start.sh 启动的
按 `Ctrl+C` 停止所有服务

### 手动启动的
在每个终端按 `Ctrl+C` 停止对应服务

## 下一步

查看 [README.md](README.md) 了解：
- 完整功能列表
- API 文档
- 开发指南
- 项目结构

开始使用 TextDiff，享受版本管理的便利！
