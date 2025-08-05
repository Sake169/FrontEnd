#!/usr/bin/env python3
"""
集成API接口
连接文档解析器和数据处理系统
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from document_parser import parse_document_from_bytes


class IntegratedDocumentProcessor:
    """集成文档处理器"""
    
    def __init__(self, output_dir: str = "./output", template_path: Optional[str] = None):
        """
        初始化集成文档处理器
        
        Args:
            output_dir: 输出目录
            template_path: Excel模板路径（可选）
        """
        self.output_dir = Path(output_dir)
        self.template_path = Path(template_path) if template_path else None
        self.output_dir.mkdir(exist_ok=True)
        
        # 验证模板文件
        if self.template_path and not self.template_path.exists():
            logger.warning(f"模板文件不存在: {self.template_path}")
            self.template_path = None
    
    def process_document(
        self, 
        file_bytes: bytes, 
        file_name: str = "document",
        file_type: Optional[str] = None,
        model_type: str = "pipeline",
        **kwargs
    ) -> Dict[str, Any]:
        """
        处理文档：解析 + 数据提取
        
        Args:
            file_bytes: 文件二进制数据
            file_name: 文件名
            file_type: 文件类型（可选，自动检测）
            model_type: 模型类型
            **kwargs: 其他参数
            
        Returns:
            处理结果字典
        """
        try:
            logger.info(f"开始处理文档: {file_name}")
            
            # 准备参数
            kwargs['template_path'] = str(self.template_path) if self.template_path else None
            
            # 调用文档解析器
            parsing_result = parse_document_from_bytes(
                file_bytes=file_bytes,
                file_name=file_name,
                file_type=file_type,
                output_dir=str(self.output_dir),
                model_type=model_type,
                **kwargs
            )
            logger.info("文档解析完成")
            
            # 构建返回结果
            result = {
                "success": True,
                "file_name": file_name,
                "parsing_result": parsing_result,
                "output_dir": str(self.output_dir)
            }
            

            # 如果有进一步处理结果，添加到返回结果中
            if 'processing_result' in parsing_result:
                result['data_extraction'] = parsing_result['processing_result']
            
            if 'processing_error' in parsing_result:
                result['processing_error'] = parsing_result['processing_error']
            
            return result
            
        except Exception as e:
            logger.error(f"文档处理失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "file_name": file_name
            }
    
    def process_document_from_file(
        self, 
        file_path: str,
        model_type: str = "pipeline",
        **kwargs
    ) -> Dict[str, Any]:
        """
        从文件路径处理文档
        
        Args:
            file_path: 文件路径
            model_type: 模型类型
            **kwargs: 其他参数
            
        Returns:
            处理结果字典
        """
        with open(file_path, 'rb') as f:
            file_bytes = f.read()
        
        return self.process_document(
            file_bytes=file_bytes,
            file_name=Path(file_path).name,
            model_type=model_type,
            **kwargs
        )


def main():
    """主函数 - 用于测试"""
    import argparse
    
    parser = argparse.ArgumentParser(description="集成文档处理器")
    parser.add_argument("input_file", help="输入文件路径")
    parser.add_argument("--output-dir", default="./output", help="输出目录")
    parser.add_argument("--template",default='/Users/jackliu/AI_Services/ai_manage/AiInvestmentFilingPlatform/backend-service/models/qwen-api-framework/filled_template.xlsx',  help="Excel模板路径")
    parser.add_argument("--model-type", default="pipeline", help="模型类型")
    
    args = parser.parse_args()
    
    # 创建处理器
    processor = IntegratedDocumentProcessor(
        output_dir=args.output_dir,
        template_path=args.template
    )
    
    # 处理文档
    result = processor.process_document_from_file(
        file_path=args.input_file,
        model_type=args.model_type
    )
    
    # 输出结果
    print(result)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main() 