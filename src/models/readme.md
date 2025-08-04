# 多模态文档解析系统

一个支持PDF、Excel、JPG等多种格式文档解析的系统，能够将多模态内容转换为Markdown格式输出。

## 功能特性

### 主函数，实现多模态的文档解析
- `main.py` - 主程序入口，提供命令行接口
- 支持批量处理和单文件处理
- 可配置输出格式（Markdown/JSON）

### 功能1: 函数接口支持pdf、excel、jpg内容的支持
- **PDF处理**: 使用PyMuPDF (fitz) 实现PDF转图像
- **文本检测**: 可以判断PDF是否文字可复制
- **Excel处理**: 支持.xlsx和.xls格式，将工作表转换为图像
- **图像处理**: 支持JPG、PNG、BMP、TIFF等格式
- **图像预处理**: 包含对比度调整、降噪、锐化等增强功能

### 功能2: 能够实现多模态内容转markdown输出
- 采用MinerU库作为底层解析方案
- 统一使用VLM-Transformers模型进行文档解析
- 支持批量图像处理
- 输出结构化的Markdown内容

### 功能3: 采用MinerU作为底层markdown解析方案
- **VLM-Transformers模型**: 统一使用，适合复杂视觉语言理解任务
- **模拟模式**: 当MinerU不可用时提供模拟处理功能

## 安装依赖

```bash
# 安装核心依赖
pip install -r requirements.txt

# 可选：安装MinerU（需要根据实际安装方式调整）
# pip install mineru
```

## 使用方法

### 命令行使用

```bash
# 基本用法
python main.py input_file.pdf

# 指定输出目录
python main.py input_file.pdf -o ./output

# 选择模型类型
python main.py input_file.pdf --model vlm-transformers

# 指定输出格式
python main.py input_file.pdf --format markdown
python main.py input_file.pdf --format json

# 启用调试模式
python main.py input_file.pdf --debug
```

### 编程接口使用

```python
from document_parser import DocumentParser
from mineru_processor import MineruProcessor
from pathlib import Path

# 初始化解析器
doc_parser = DocumentParser(dpi=300)
mineru_processor = MineruProcessor(model_type='vlm-transformers')

# 处理PDF文件
pdf_path = Path("document.pdf")
images = doc_parser.pdf_to_images(pdf_path)

# 转换为Markdown
markdown_content = mineru_processor.process_images(images)

# 保存结果
with open("output.md", "w", encoding="utf-8") as f:
    f.write(markdown_content)
```

### 运行示例

```bash
# 运行示例脚本
python example.py
```

## 支持的文件格式

- **PDF**: `.pdf`
- **Excel**: `.xlsx`, `.xls`
- **图像**: `.jpg`, `.jpeg`, `.png`, `.bmp`, `.tiff`, `.tif`

## 项目结构

```
ai_manage/
├── main.py                 # 主程序入口
├── document_parser.py      # 文档解析器
├── mineru_processor.py     # MinerU处理器
├── utils.py               # 工具函数
├── example.py             # 示例脚本
├── requirements.txt       # 依赖列表
├── readme.md             # 说明文档
├── api_qwen.py           # 原有的API文件
├── output/               # 输出目录
└── test/                 # 测试文件目录
```

## 配置选项

### 文档解析器配置
- `dpi`: 图像分辨率（默认300）
- 图像预处理参数（对比度、亮度、降噪等）

### MinerU模型配置
- `model_type`: 模型类型（统一使用vlm-transformers）
- `model_config`: 模型特定配置参数

## 输出格式

### Markdown格式
- 结构化的文档内容
- 包含文件信息和处理元数据
- 支持表格、列表等格式

### JSON格式
- 包含源文件信息
- 处理时间戳
- 结构化内容数据

## 错误处理

- 文件验证和错误检查
- 详细的日志记录
- 优雅的错误恢复
- 模拟模式支持

## 性能优化

- 批量处理支持
- 图像预处理优化
- 内存使用优化
- 进度显示

## 开发说明

### 添加新的文件格式支持
1. 在 `document_parser.py` 中添加新的处理方法
2. 在 `utils.py` 中更新支持格式列表
3. 在 `main.py` 中添加相应的处理逻辑

### 扩展MinerU功能
1. 在 `mineru_processor.py` 中修改模型配置
2. 实现相应的处理方法
3. 更新配置选项

## 故障排除

### 常见问题

1. **MinerU库不可用**
   - 系统会自动切换到模拟模式
   - 安装MinerU库以获得完整功能

2. **PDF处理失败**
   - 检查PDF文件是否损坏
   - 确认PyMuPDF已正确安装

3. **图像处理错误**
   - 检查图像文件格式是否支持
   - 确认OpenCV和Pillow已安装

### 日志调试

```bash
# 启用详细日志
python main.py input_file.pdf --debug
```

## 许可证

本项目采用MIT许可证。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。