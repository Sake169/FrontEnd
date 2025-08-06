# Excel编辑器前端应用

一个基于React和AG Grid的现代化Excel编辑器前端应用，提供强大的表格编辑和数据可视化功能。

## 🚀 技术栈

- **React 18** - 现代化的前端框架
- **TypeScript** - 类型安全的JavaScript
- **AG Grid** - 企业级表格组件
- **Vite** - 快速的构建工具
- **Tailwind CSS** - 实用优先的CSS框架
- **Axios** - HTTP客户端

## 📁 项目结构

```
frontend-app/
├── src/
│   ├── components/          # 可复用组件
│   │   ├── ExcelEditor.tsx  # Excel编辑器主组件
│   │   ├── FileUpload.tsx   # 文件上传组件
│   │   └── Layout.tsx       # 布局组件
│   ├── services/            # API服务
│   │   ├── api.ts          # API配置
│   │   ├── fileService.ts  # 文件服务
│   │   └── excelService.ts # Excel服务
│   ├── types/              # TypeScript类型定义
│   │   ├── excel.ts        # Excel相关类型
│   │   └── api.ts          # API相关类型
│   ├── utils/              # 工具函数
│   │   ├── constants.ts    # 常量定义
│   │   └── helpers.ts      # 辅助函数
│   ├── hooks/              # 自定义Hooks
│   │   └── useExcel.ts     # Excel操作Hook
│   ├── App.tsx             # 主应用组件
│   ├── main.tsx            # 应用入口
│   └── index.css           # 全局样式
├── public/                 # 静态资源
├── index.html              # HTML模板
├── package.json            # 项目配置
├── tsconfig.json           # TypeScript配置
├── vite.config.js          # Vite配置
└── README.md               # 项目说明
```

## 🛠️ 安装与运行

### 环境要求

- Node.js >= 16.0.0
- npm >= 8.0.0 或 yarn >= 1.22.0

### 安装依赖

```bash
# 使用npm
npm install

# 或使用yarn
yarn install
```

### 开发模式

```bash
# 启动开发服务器
npm run dev

# 或
yarn dev
```

应用将在 `http://localhost:3000` 启动

### 生产构建

```bash
# 构建生产版本
npm run build

# 预览生产版本
npm run preview
```

## 🎯 主要功能

### Excel编辑器
- ✅ 表格数据展示和编辑
- ✅ 单元格内容修改
- ✅ 行列操作（添加、删除、移动）
- ✅ 数据排序和筛选
- ✅ 复制粘贴功能
- ✅ 撤销重做操作
- ✅ 数据验证
- ✅ 格式化支持

### 文件操作
- ✅ Excel文件上传
- ✅ 文件保存和下载
- ✅ 多种文件格式支持
- ✅ 文件预览
- ✅ 批量文件处理

### 数据处理
- ✅ 数据导入导出
- ✅ 数据清洗和转换
- ✅ 统计分析
- ✅ 图表生成
- ✅ 数据可视化

### 用户界面
- ✅ 响应式设计
- ✅ 现代化UI
- ✅ 主题切换
- ✅ 快捷键支持
- ✅ 多语言支持

## 🔧 配置

### 环境变量

创建 `.env` 文件：

```env
# API配置
VITE_API_BASE_URL=http://localhost:8001/api/v1
VITE_API_TIMEOUT=30000

# 应用配置
VITE_APP_TITLE=Excel编辑器
VITE_APP_VERSION=1.0.0

# 功能开关
VITE_ENABLE_AI_FEATURES=true
VITE_ENABLE_CLOUD_SYNC=false

# 文件上传配置
VITE_MAX_FILE_SIZE=10485760  # 10MB
VITE_ALLOWED_FILE_TYPES=.xlsx,.xls,.csv
```

### AG Grid配置

```typescript
// AG Grid主题和配置
const gridOptions = {
  theme: 'ag-theme-alpine',
  enableRangeSelection: true,
  enableCharts: true,
  enableClipboard: true,
  enableFillHandle: true,
  undoRedoCellEditing: true,
  undoRedoCellEditingLimit: 20
};
```

## 📡 API集成

### 后端服务连接

前端应用通过RESTful API与后端服务通信：

```typescript
// API服务配置
const apiConfig = {
  baseURL: process.env.VITE_API_BASE_URL,
  timeout: parseInt(process.env.VITE_API_TIMEOUT || '30000'),
  headers: {
    'Content-Type': 'application/json'
  }
};
```

### 主要API端点

- `POST /upload/` - 文件上传
- `GET /excel/files` - 获取文件列表
- `POST /excel/save` - 保存Excel数据
- `GET /excel/download/{filename}` - 下载文件
- `POST /ai/process` - AI数据处理

## 🎨 样式和主题

### Tailwind CSS配置

```javascript
// tailwind.config.js
module.exports = {
  content: ['./src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#3b82f6',
        secondary: '#64748b',
        accent: '#f59e0b'
      }
    }
  },
  plugins: []
};
```

### AG Grid主题定制

```css
/* 自定义AG Grid样式 */
.ag-theme-alpine {
  --ag-header-background-color: #f8fafc;
  --ag-header-foreground-color: #374151;
  --ag-border-color: #e5e7eb;
  --ag-row-hover-color: #f3f4f6;
}
```

## 🧪 测试

```bash
# 运行单元测试
npm run test

# 运行测试覆盖率
npm run test:coverage

# 运行E2E测试
npm run test:e2e
```

## 📦 部署

### 静态部署

```bash
# 构建生产版本
npm run build

# 部署到静态服务器
# 将 dist/ 目录内容上传到服务器
```

### Docker部署

```dockerfile
# Dockerfile
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 🔍 性能优化

### 代码分割

```typescript
// 路由级别的代码分割
const ExcelEditor = lazy(() => import('./components/ExcelEditor'));
const FileUpload = lazy(() => import('./components/FileUpload'));
```

### 虚拟滚动

```typescript
// AG Grid虚拟滚动配置
const gridOptions = {
  rowModelType: 'infinite',
  cacheBlockSize: 100,
  maxBlocksInCache: 10
};
```

## 🐛 故障排除

### 常见问题

1. **AG Grid样式问题**
   - 确保正确导入CSS文件
   - 检查主题类名是否正确应用

2. **文件上传失败**
   - 检查文件大小限制
   - 验证文件类型是否支持
   - 确认后端服务是否运行

3. **API连接问题**
   - 检查环境变量配置
   - 验证后端服务地址
   - 查看浏览器控制台错误

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 支持

如有问题或建议，请：

- 创建 [Issue](../../issues)
- 发送邮件至：support@example.com
- 查看 [文档](../../wiki)

---

**注意**: 这是一个前后端分离的项目，需要配合后端服务使用。请确保后端服务正常运行后再启动前端应用。