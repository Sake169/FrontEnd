# 证券公司员工配偶信息报备系统 - 后端服务

## 项目概述

本项目是证券公司员工配偶信息报备系统的后端服务，主要负责：
- 文件上传处理
- AI大模型调用
- Excel文件生成和处理
- API接口服务

## 技术栈

- **框架**: FastAPI
- **数据处理**: Pandas
- **文件处理**: aiofiles
- **AI集成**: 预留大模型接口
- **部署**: Uvicorn

## 项目结构

```
backend-service/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI应用入口
│   ├── api/                 # API路由模块
│   │   ├── __init__.py
│   │   ├── upload.py        # 文件上传接口
│   │   ├── excel.py         # Excel处理接口
│   │   └── ai.py            # AI模型调用接口
│   ├── core/                # 核心配置
│   │   ├── __init__.py
│   │   ├── config.py        # 应用配置
│   │   └── dependencies.py  # 依赖注入
│   ├── models/              # 数据模型
│   │   ├── __init__.py
│   │   ├── upload.py        # 上传相关模型
│   │   └── excel.py         # Excel相关模型
│   ├── services/            # 业务逻辑服务
│   │   ├── __init__.py
│   │   ├── file_service.py  # 文件处理服务
│   │   ├── excel_service.py # Excel处理服务
│   │   └── ai_service.py    # AI服务
│   └── utils/               # 工具函数
│       ├── __init__.py
│       └── file_utils.py    # 文件工具
├── uploads/                 # 上传文件目录
├── outputs/                 # 输出文件目录
├── requirements.txt         # Python依赖
├── .env                     # 环境变量
├── .gitignore              # Git忽略文件
└── README.md               # 项目说明
```

## 安装和运行

### 1. 安装依赖

```bash
cd backend-service
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 到 `.env` 并配置相关参数。

### 3. 运行服务

```bash
# 开发模式
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# 生产模式
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

## API文档

启动服务后，访问以下地址查看API文档：
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## 主要功能

### 1. 文件上传
- 支持图片和PDF文件上传
- 文件类型验证
- 异步文件处理

### 2. AI识别
- 集成大模型API
- 图片/PDF内容识别
- 结构化数据提取

### 3. Excel处理
- 动态Excel生成
- 数据编辑和保存
- 文件下载服务

## 开发指南

### 添加新的API接口

1. 在 `app/api/` 目录下创建新的路由文件
2. 在 `app/models/` 中定义数据模型
3. 在 `app/services/` 中实现业务逻辑
4. 在 `app/main.py` 中注册路由

### 环境配置

所有配置项都在 `app/core/config.py` 中管理，支持环境变量覆盖。

## 部署

### Docker部署

```bash
# 构建镜像
docker build -t backend-service .

# 运行容器
docker run -p 8001:8001 backend-service
```

### 生产环境

建议使用 Gunicorn + Uvicorn 进行生产部署：

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
```