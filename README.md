# 证券公司员工配偶信息报备系统

一个基于 React + FastAPI 的现代化证券报备管理系统，支持文件上传、AI识别、Excel处理和用户管理功能。

## 🏗️ 项目结构

```
FrontEnd/
├── frontend-app/           # 前端应用 (React + TypeScript + Material-UI)
│   ├── src/
│   │   ├── components/     # 可复用组件
│   │   ├── pages/         # 页面组件
│   │   ├── contexts/      # React Context
│   │   ├── services/      # API服务
│   │   └── ...
│   ├── package.json
│   └── vite.config.js
├── backend-service/        # 后端服务 (FastAPI + SQLAlchemy)
│   ├── app/
│   │   ├── api/           # API路由
│   │   ├── core/          # 核心配置
│   │   ├── models/        # 数据模型
│   │   ├── services/      # 业务服务
│   │   └── main.py        # 主应用
│   ├── requirements.txt
│   └── start.py           # 启动脚本
├── package.json           # 根目录配置（统一启动脚本）
└── README.md
```

## ✨ 主要功能

### 🔐 用户认证系统
- 用户登录/注册
- 基于JWT的身份验证
- 角色权限管理（管理员/普通用户）
- 用户信息管理

### 📁 文件处理
- 支持图片和PDF文件上传
- AI智能识别文档内容
- 自动生成Excel报表
- 文件下载和管理

### 👨‍👩‍👧‍👦 家属亲戚管理
- 家属信息录入和管理
- 关系维护
- 信息查询和编辑

### 📊 证券填报管理
- 证券交易信息录入
- 报表生成和导出
- 数据统计和分析

### 🎛️ 管理员功能
- 用户管理
- 系统配置
- 数据统计
- 日志查看

## 🚀 快速开始

### 环境要求

- Node.js 16+
- Python 3.8+
- npm 或 yarn

### 1. 克隆项目

```bash
git clone <repository-url>
cd FrontEnd
```

### 2. 安装依赖

```bash
# 安装根目录依赖（包含启动脚本）
npm install

# 安装前端依赖
cd frontend-app
npm install
cd ..

# 安装后端依赖
cd backend-service
pip install -r requirements.txt
cd ..
```

### 3. 启动服务

#### 方式一：一键启动（推荐）
```bash
# 同时启动前端和后端
npm start
```

#### 方式二：分别启动
```bash
# 启动后端服务 (端口 8001)
npm run backend

# 启动前端服务 (端口 3000)
npm run dev
```

### 4. 访问应用

- 前端应用: http://localhost:3000
- 后端API: http://localhost:8001
- API文档: http://localhost:8001/docs

## 🔧 开发指南

### 前端开发

```bash
cd frontend-app
npm run dev     # 开发模式
npm run build   # 构建生产版本
npm run preview # 预览生产版本
```

### 后端开发

```bash
cd backend-service
python start.py  # 启动开发服务器
```

### 代码规范

```bash
# 前端代码检查
npm run lint
npm run lint:fix
```

## 📝 API文档

启动后端服务后，访问 http://localhost:8001/docs 查看完整的API文档。

### 主要API端点

- `POST /api/v1/auth/login` - 用户登录
- `GET /api/v1/auth/me` - 获取当前用户信息
- `POST /api/v1/upload` - 文件上传
- `GET /api/v1/family-members` - 获取家属列表
- `POST /api/v1/securities-reports` - 创建证券报告

## 🔒 安全特性

- JWT身份验证
- 密码加密存储
- CORS跨域保护
- 文件类型验证
- SQL注入防护

## 🛠️ 技术栈

### 前端
- **React 18** - 用户界面框架
- **TypeScript** - 类型安全
- **Material-UI** - UI组件库
- **React Router** - 路由管理
- **Axios** - HTTP客户端
- **Vite** - 构建工具

### 后端
- **FastAPI** - 现代Python Web框架
- **SQLAlchemy** - ORM数据库操作
- **Pydantic** - 数据验证
- **JWT** - 身份验证
- **Uvicorn** - ASGI服务器

## 📦 部署

### 生产环境部署

1. 构建前端
```bash
cd frontend-app
npm run build
```

2. 配置后端环境变量
```bash
cp backend-service/.env.example backend-service/.env
# 编辑 .env 文件配置生产环境参数
```

3. 启动生产服务
```bash
# 后端
cd backend-service
uvicorn app.main:app --host 0.0.0.0 --port 8001

# 前端（使用nginx等静态服务器）
# 将 frontend-app/dist 目录部署到静态服务器
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🆘 常见问题

### Q: 登录后直接跳转到证券报备页面？
A: 这是因为之前的项目结构混乱导致的。重构后，未登录用户会正确跳转到登录页面。

### Q: 为什么有多个前端/后端目录？
A: 已经清理了冗余目录，现在统一使用 `frontend-app` 作为前端，`backend-service` 作为后端。

### Q: 如何添加新的页面？
A: 在 `frontend-app/src/pages/` 目录下创建新组件，然后在 `App.tsx` 中添加路由配置。

### Q: 如何添加新的API端点？
A: 在 `backend-service/app/api/` 目录下创建或修改路由文件，然后在 `main.py` 中注册路由。