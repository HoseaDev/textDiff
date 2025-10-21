# TextDiff - 文本版本管理与差异比较系统

一个功能完整的文本版本管理和差异比较系统，支持自动/手动保存、版本对比、实时协作等功能。

## 功能特性

### 核心功能
- ✅ **多版本管理**：自动保存每次修改，生成完整版本历史
- ✅ **智能差异对比**：支持字符级、单词级、行级、语义级多种对比模式
- ✅ **灵活的保存策略**：支持手动保存、自动保存、混合模式
- ✅ **版本回溯**：可恢复到任意历史版本
- ✅ **版本标签**：为重要版本添加标记和说明
- ✅ **实时协作**：WebSocket 支持多用户在线协作（可选）

### 技术特性
- 🎨 **响应式设计**：完美适配桌面、平板、手机
- ⚡ **高性能**：防抖优化、虚拟滚动、缓存机制
- 🔒 **类型安全**：全栈 TypeScript 支持
- 🎯 **清晰架构**：模块化设计，易于扩展

## 技术栈

### 后端
- **框架**：FastAPI
- **数据库**：SQLAlchemy + SQLite (开发) / PostgreSQL (生产)
- **WebSocket**：FastAPI WebSocket
- **差异算法**：Python difflib

### 前端
- **框架**：Vue 3 + TypeScript
- **构建工具**：Vite
- **状态管理**：Pinia
- **路由**：Vue Router
- **样式**：SCSS + 响应式设计

## 快速开始

### 前置要求
- Python 3.11+
- Node.js 18+
- npm 或 yarn

### 1. 克隆项目
```bash
cd /Users/harry/PycharmProjects/TextDiff
```

### 2. 后端设置

```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 复制环境配置
cp .env.example .env

# 启动后端服务
python -m app.main
```

后端服务将运行在 `http://localhost:8000`

API 文档：`http://localhost:8000/docs`

### 3. 前端设置

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端应用将运行在 `http://localhost:5173`

## 项目结构

```
TextDiff/
├── backend/                 # 后端代码
│   ├── app/
│   │   ├── api/            # API 路由
│   │   ├── models/         # 数据库模型
│   │   ├── services/       # 业务逻辑
│   │   ├── schemas/        # Pydantic 模式
│   │   ├── core/           # 核心配置
│   │   └── main.py         # 应用入口
│   ├── requirements.txt    # Python 依赖
│   └── .env.example        # 环境配置示例
│
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── components/    # Vue 组件
│   │   ├── views/         # 页面视图
│   │   ├── stores/        # Pinia 状态管理
│   │   ├── api/           # API 客户端
│   │   ├── types/         # TypeScript 类型
│   │   ├── router/        # 路由配置
│   │   └── assets/        # 静态资源
│   ├── package.json       # Node 依赖
│   └── vite.config.ts     # Vite 配置
│
└── README.md              # 项目文档
```

## 使用指南

### 保存模式

1. **手动保存模式**
   - 点击保存按钮或按 `Ctrl+S` 保存
   - 适合需要完全控制保存时机的场景

2. **自动保存模式**
   - 系统自动定期保存（默认30秒）
   - 防止数据丢失

3. **混合模式**（推荐）
   - 同时支持手动和自动保存
   - 灵活性最高

### 版本对比

1. 在版本列表中选择任意版本
2. 点击"查看差异"按钮
3. 选择对比模式：
   - **智能对比**：结合行级和字符级，推荐使用
   - **行级对比**：快速定位变化的行
   - **单词对比**：查看单词级别的变化
   - **字符对比**：最细粒度的对比

### 版本恢复

1. 在版本列表中选择要恢复的版本
2. 点击"恢复"按钮
3. 系统会创建一个新版本，内容与选择的版本相同

## API 文档

### 主要端点

#### 文档管理
- `POST /api/documents` - 创建文档
- `GET /api/documents` - 获取文档列表
- `GET /api/documents/{id}` - 获取文档详情
- `PUT /api/documents/{id}` - 更新文档
- `DELETE /api/documents/{id}` - 删除文档

#### 版本管理
- `POST /api/documents/{id}/versions` - 创建版本
- `GET /api/documents/{id}/versions` - 获取版本列表
- `GET /api/documents/{id}/versions/{vid}` - 获取版本详情
- `POST /api/documents/{id}/restore/{vid}` - 恢复版本

#### 差异比较
- `GET /api/diff/{vid1}/{vid2}` - 比较两个版本
- `GET /api/diff/document/{id}/latest/{vid}` - 与最新版本比较

完整 API 文档：访问 `http://localhost:8000/docs`

## 移动端适配

系统完全响应式设计，支持：
- 📱 手机端（<480px）
- 📲 平板端（480px-768px）
- 💻 桌面端（>768px）

### 移动端特性
- 侧边栏自动折叠为抽屉菜单
- 触控友好的按钮和交互
- 自适应字体大小
- 简化的界面布局

## 配置说明

### 后端配置 (.env)

```bash
# 数据库
DATABASE_URL=sqlite:///./textdiff.db

# JWT 密钥
SECRET_KEY=your-secret-key

# CORS
ALLOWED_ORIGINS=["http://localhost:5173"]
```

### 前端配置 (vite.config.ts)

```typescript
server: {
  proxy: {
    '/api': 'http://localhost:8000',
    '/ws': 'ws://localhost:8000'
  }
}
```

## 开发指南

### 添加新功能

1. **后端**：
   - 在 `models/` 添加数据模型
   - 在 `services/` 实现业务逻辑
   - 在 `api/routes/` 添加 API 端点

2. **前端**：
   - 在 `components/` 创建 Vue 组件
   - 在 `stores/` 添加状态管理
   - 在 `api/` 添加 API 调用

### 代码规范

- 使用 TypeScript 类型注解
- 遵循组件化设计
- 保持代码简洁和可读性
- 添加必要的注释

## 性能优化

- ✅ 防抖处理（自动保存）
- ✅ 内容哈希检测（避免重复保存）
- ✅ 虚拟滚动（大列表）
- ✅ 懒加载（按需加载）
- ✅ 缓存策略（减少请求）

## 常见问题

### 1. 后端启动失败
检查 Python 版本和依赖安装是否正确

### 2. 前端连接失败
确认后端服务已启动且端口正确（8000）

### 3. 保存不生效
检查网络连接和浏览器控制台错误信息

## 未来规划

- [ ] 多文档管理界面
- [ ] Markdown 实时预览
- [ ] 代码语法高亮
- [ ] 协作编辑冲突解决
- [ ] 导出版本历史（PDF/HTML）
- [ ] 全文搜索
- [ ] 用户权限管理

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题或建议，请通过 Issue 联系。
