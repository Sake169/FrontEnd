import sys
import json
from pathlib import Path
from typing import Dict
import re
from bs4 import BeautifulSoup
from services.table_service import TableExtractionService
from utils.logger import setup_logger

logger = setup_logger()

def extract_text_from_html(html_content: str) -> str:
    """从HTML内容中提取纯文本"""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        # 移除所有脚本和样式
        for script in soup(["script", "style"]):
            script.decompose()
        # 获取文本并清理
        text = soup.get_text(separator='\n')
        # 去除多余空行和空白字符
        lines = (line.strip() for line in text.splitlines())
        return '\n'.join(line for line in lines if line)
    except Exception as e:
        logger.warning(f"HTML解析失败: {str(e)}")
        return html_content  # 解析失败返回原始内容

def read_files(input_path: Path) -> list:
    """读取所有MD和HTML文件内容"""
    files_data = []
    
    # 支持的扩展名
    valid_extensions = ('.md', '.html', '.htm')
    
    if input_path.is_file() and input_path.suffix.lower() in valid_extensions:
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if input_path.suffix.lower() in ('.html', '.htm'):
                    content = extract_text_from_html(content)
                files_data.append({
                    "filename": input_path.name,
                    "content": content
                })
        except Exception as e:
            logger.error(f"读取文件失败 {input_path.name}: {str(e)}")
    elif input_path.is_dir():
        for file_path in input_path.glob('*'):
            if file_path.suffix.lower() in valid_extensions:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if file_path.suffix.lower() in ('.html', '.htm'):
                            content = extract_text_from_html(content)
                        files_data.append({
                            "filename": file_path.name,
                            "content": content
                        })
                except Exception as e:
                    logger.error(f"读取文件失败 {file_path.name}: {str(e)}")
    
    return files_data

def process_files(input_path: Path, output_dir: Path, template_path: Path):
    """处理文件并生成类型化报告"""
    files_data = read_files(input_path)
    if not files_data:
        logger.error("未找到可处理的文件")
        return False
    
    combined_content = "\n\n".join(
        f"文件: {item['filename']}\n内容:\n{item['content']}" 
        for item in files_data
    )
    
    service = TableExtractionService()
    try:
        # 提取结构化数据
        result = service.extract_typed_records(combined_content)
        
        # 保存JSON报告
        json_path = output_dir / "typed_report.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # 写入Excel模板
        excel_path = output_dir / "filled_template.xlsx"
        if service.write_to_excel_template(result, template_path, excel_path):
            logger.info(f"Excel报告已生成: {excel_path}")
        
        logger.info(f"处理成功，报告已生成到: {output_dir}")
        return True
        
    except Exception as e:
        logger.error(f"处理失败: {str(e)}", exc_info=True)
        return False

def main():
    if len(sys.argv) < 2:
        print("""
使用方法:
  python main.py 输入路径 [输出路径] [模板路径]
  
参数说明:
  输入路径: 可以是单个文件(.md/.html)或包含多个文件的目录
  输出路径: (可选) 输出目录，默认为'output'
  模板路径: (可选) Excel模板路径，默认为'filled_template.xlsx'
""")
        return
    
    input_path = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("output")
    template_path = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("filled_template.xlsx")
    
    output_dir.mkdir(exist_ok=True)
    
    if not template_path.exists():
        logger.error(f"模板文件不存在: {template_path}")
        return
    
    process_files(input_path, output_dir, template_path)

if __name__ == "__main__":
    main()