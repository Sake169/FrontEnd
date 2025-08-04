# 多模态文档解析系统

一个支持PDF、Excel、JPG等多种格式文档解析的系统，能够将多模态内容转换为Markdown格式输出。

## 功能特性

### 主函数，实现多模态的文档解析
- `parse_document_from_bytes.py` - 主程序入口，接受二进制文档
- 支持文件类型检测
- 支持多种编码格式输入：jpg、jpeg、xlsx、pdf

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

## 安装依赖

```bash
# 安装核心依赖
pip install -r requirements.txt

# 可选：安装MinerU（需要根据实际安装方式调整）
# pip install mineru
```