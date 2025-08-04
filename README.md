# Excel编辑器 - 前后端分离项目

一个现代化的Excel编辑器应用，采用前后端分离架构，提供强大的表格编辑、数据处理和AI分析功能。

## 功能特性

- 📁 **文件上传**: 支持图片（JPG、PNG、GIF等）和PDF文件上传
- 👥 **信息填写**: 配偶/利害关系人详细信息录入
- 🤖 **AI识别**: 后端集成大模型接口识别交易截图内容（当前为模拟实现）
- 📊 **Excel生成**: 自动生成结构化Excel报表
- ✏️ **在线编辑**: 支持Excel文件在线编辑功能
- 💾 **文件下载**: 支持编辑后的Excel文件下载
- 📱 **响应式设计**: 适配桌面端和移动端

## 技术栈

### 前端
- React 18
- Ant Design Pro
- TypeScript
- Vite
- Axios
- XLSX.js
- File-saver

### 后端
- FastAPI
- Python 3.8+
- Pandas
- OpenPyXL
- Uvicorn
- Pydantic

## 项目结构

```
FrontEnd/
├── src/                    # 前端源码
│   ├── components/         # 组件
│   │   ├── ExcelEditor.tsx # Excel编辑器
│   │   └── FileUpload.tsx  # 文件上传组件
│   ├── pages/             # 页面
│   │   └── FileUploadPage.tsx
│   ├── services/          # API服务
│   │   └── api.ts
│   ├── App.tsx            # 主应用组件
│   ├── main.tsx           # 入口文件
│   └── index.css          # 全局样式
├── backend/               # 后端源码
│   ├── main.py           # FastAPI主应用
│   ├── start.py          # 启动脚本
│   └── requirements.txt  # Python依赖
├── example.xlsx          # 示例Excel文件
├── package.json          # 前端依赖配置
├── vite.config.js        # Vite配置
├── tsconfig.json         # TypeScript配置
└── README.md             # 项目说明
```

## 快速开始

### 环境要求

- Node.js 16+ 
- Python 3.8+
- npm 或 yarn

### 1. 安装前端依赖

```bash
# 在项目根目录下
npm install
# 或
yarn install
```

### 2. 安装后端依赖

```bash
# 进入后端目录
cd backend

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 启动后端服务

```bash
# 在 backend 目录下
python start.py

# 或直接使用 uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

后端服务将在 http://localhost:8000 启动

API文档地址: http://localhost:8000/docs

### 4. 启动前端服务

```bash
# 在项目根目录下
npm run dev
# 或
yarn dev
```

前端服务将在 http://localhost:3000 启动

## 使用说明

### 1. 文件上传

1. 打开浏览器访问 http://localhost:3000
2. 在上传区域选择或拖拽图片/PDF文件
3. 填写相关人员信息：
   - 姓名
   - 与员工关系（配偶、子女、父母等）
   - 身份证号码
   - 联系电话
   - 备注说明（可选）
4. 点击"上传并处理"按钮

### 2. Excel编辑

1. 文件上传成功后，系统会自动跳转到Excel编辑页面
2. 可以直接在表格中编辑单元格内容
3. 点击"保存"按钮保存修改
4. 点击"下载"按钮下载Excel文件

### 3. 重新处理

在任何阶段都可以点击"重新开始"或相关链接重新上传文件

## API接口

### 主要接口

- `POST /upload` - 文件上传和处理
- `GET /download/{filename}` - 文件下载
- `POST /save-excel` - 保存Excel数据
- `GET /files` - 获取文件列表
- `GET /health` - 健康检查

详细API文档请访问: http://localhost:8000/docs

## 开发说明

### 前端开发

```bash
# 开发模式
npm run dev

# 构建生产版本
npm run build

# 预览生产版本
npm run preview

# 代码检查
npm run lint

# 代码格式化
npm run lint:fix
```

### 后端开发

```bash
# 开发模式（自动重载）
python start.py

# 或使用uvicorn
uvicorn main:app --reload
```

### 扩展功能

当前系统为最小化demo，后续可扩展的功能包括：

1. **AI模型集成**: 在 `main.py` 的 `/upload` 接口中集成实际的图片/PDF识别模型
2. **用户认证**: 添加用户登录、权限管理
3. **数据库存储**: 集成数据库存储用户信息和处理记录
4. **文件管理**: 完善的文件管理和版本控制
5. **审批流程**: 添加报备审批工作流
6. **数据统计**: 添加报表统计和数据分析功能

## 故障排除

### 常见问题

1. **前端无法连接后端**
   - 确保后端服务已启动（http://localhost:8000）
   - 检查 `vite.config.js` 中的代理配置

2. **文件上传失败**
   - 检查文件大小（限制10MB）
   - 确认文件格式（支持图片和PDF）
   - 查看后端控制台错误信息

3. **Excel文件无法下载**
   - 确保 `example.xlsx` 文件存在于项目根目录
   - 检查后端 `outputs` 目录权限

4. **依赖安装失败**
   - 更新 npm/pip 到最新版本
   - 清除缓存后重新安装
   - 检查网络连接和镜像源配置

### 日志查看

- 前端日志：浏览器开发者工具 Console
- 后端日志：终端输出

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request 来改进项目。

## 联系方式

如有问题或建议，请通过以下方式联系：

- 项目Issues: [GitHub Issues]()
- 邮箱: [your-email@example.com]()