import sys
import json
from pathlib import Path
from typing import Dict, List, Any
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

def process_markdown_content(markdown_content: str, output_dir: Path, template_path: Path) -> Dict[str, Any]:
    """
    处理markdown内容并生成类型化报告
    
    Args:
        markdown_content: markdown格式的内容
        output_dir: 输出目录
        template_path: Excel模板路径
        
    Returns:
        处理结果字典
    """
    try:
        # 提取HTML表格中的纯文本
        if '<table>' in markdown_content:
            markdown_content = extract_text_from_html(markdown_content)
        
        service = TableExtractionService()
        
        # 提取结构化数据
        result = service.extract_typed_records(markdown_content)

        # 保存JSON报告
        json_path = output_dir / "typed_report.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # 写入Excel模板
        excel_path = "/Users/jackliu/AI_Services/ai_manage/AiInvestmentFilingPlatform/output/filled_template.xlsx"
        if service.write_to_excel_template(result, template_path, excel_path):
            logger.info(f"Excel报告已生成: {excel_path}")
        
        logger.info(f"处理成功，报告已生成到: {output_dir}")
        return {
            "success": True,
            "json_report": str(json_path),
            "excel_report": str(excel_path),
            "extracted_data": result
        }
        
    except Exception as e:
        logger.error(f"处理失败: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }

def process_document_parsing_result(parsing_result: Dict[str, Any], output_dir: Path, template_path: Path) -> Dict[str, Any]:
    """
    处理文档解析结果
    
    Args:
        parsing_result: 文档解析器返回的结果
        output_dir: 输出目录
        template_path: Excel模板路径
        
    Returns:
        处理结果字典
    """
    try:
        if not parsing_result or 'text_list' not in parsing_result:
            return {"success": False, "error": "无效的解析结果"}
        
        # 合并所有文件的文本内容
        combined_content = ""
        for text_item in parsing_result['text_list']:
            file_type = text_item.get('file_type', 'unknown')
            file_text = text_item.get('file_text', '')
            combined_content += f"\n\n文件类型: {file_type}\n内容:\n{file_text}"
        
        # 处理合并后的内容
        return process_markdown_content(combined_content, output_dir, template_path)
        
    except Exception as e:
        logger.error(f"处理文档解析结果失败: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }

def main():
    """主函数 - 用于测试"""
    if len(sys.argv) < 2:
        print("""
使用方法:
  python main.py 输入路径 [输出路径] [模板路径]
  
参数说明:
  输入路径: markdown文件路径
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
    
    # 读取markdown文件
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        result = process_markdown_content(markdown_content, output_dir, template_path)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        logger.error(f"处理失败: {str(e)}")
        print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()