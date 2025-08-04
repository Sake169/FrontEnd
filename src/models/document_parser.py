"""
文档解析器模块
支持PDF、Excel、JPG等多种格式文档解析，将多模态内容转换为Markdown格式输出
"""

import uuid
import os
import tempfile
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
from loguru import logger
import json

# MinerU相关导入
from mineru.cli.common import do_parse, read_fn, pdf_suffixes, image_suffixes, prepare_env
import re


def safe_stem(file_path):
    """安全的文件名stem处理，只保留字母、数字、下划线和点"""
    stem = Path(file_path).stem
    return re.sub(r'[^\w.]', '_', stem)


class DocumentParser:
    """文档解析器，支持PDF、Excel、JPG等多种格式"""
    
    def __init__(self, dpi: int = 300, output_dir: str = "./output"):
        """
        初始化文档解析器
        
        Args:
            dpi: 图像分辨率，默认300
            output_dir: 输出目录，默认"./output"
        """
        self.dpi = dpi
        self.output_dir = output_dir
        self.supported_formats = pdf_suffixes + image_suffixes + ['.xlsx', '.xls']
        
    def is_supported_format(self, file_path: Union[str, Path]) -> bool:
        """检查文件格式是否支持"""
        file_path = Path(file_path)
        return file_path.suffix.lower() in self.supported_formats
    
    def process_excel_to_images(self, file_path: Union[str, Path]) -> List[bytes]:
        """将Excel文件转换为图像字节数据"""
        try:
            # 这里可以实现Excel转图像的逻辑
            # 目前暂时抛出提示，需要额外的Excel处理依赖
            raise NotImplementedError("Excel处理功能需要额外的依赖库，请先实现Excel转图像功能")
        except Exception as e:
            logger.error(f"Excel文件处理失败: {str(e)}")
            raise
    
    def load_file_bytes(self, file_path: Union[str, Path]) -> bytes:
        """
        加载文件字节数据
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件的字节数据
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        if not self.is_supported_format(file_path):
            raise ValueError(f"不支持的文件格式: {file_path.suffix}")
        
        # 对于Excel文件，需要特殊处理
        if file_path.suffix.lower() in ['.xlsx', '.xls']:
            # 目前暂不实现Excel处理，抛出提示
            raise NotImplementedError("Excel处理功能待实现")
        
        # 使用MinerU的read_fn函数处理PDF和图像文件
        return read_fn(file_path)


class MineruProcessor:
    """MinerU处理器，使用VLM-Transformers模型进行文档解析"""
    
    def __init__(self, model_type: str = "vlm-transformers", **config):
        """
        初始化MinerU处理器
        
        Args:
            model_type: 模型类型，默认"vlm-transformers"
            **config: 其他配置参数
        """
        self.model_type = model_type
        self.config = {
            "lang_list": ["ch"],
            "backend": model_type,
            "parse_method": "auto",
            "formula_enable": True,
            "table_enable": True,
            "server_url": None,
            "return_md": True,
            "return_middle_json": False,
            "return_model_output": False,
            "return_content_list": False,
            "start_page_id": 0,
            "end_page_id": None,
        }
        self.config.update(config)
    
    def process_files(
        self,
        file_bytes_list: List[bytes],
        file_names: List[str],
        output_dir: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        处理文件字节数据列表
        
        Args:
            file_bytes_list: 文件字节数据列表
            file_names: 文件名列表
            output_dir: 输出目录
            **kwargs: 其他参数
            
        Returns:
            处理结果字典
        """
        # 合并配置
        config = {**self.config, **kwargs}
        
        # 确保语言列表长度与文件数量一致
        lang_list = config["lang_list"]
        if len(lang_list) != len(file_names):
            lang_list = [lang_list[0] if lang_list else "ch"] * len(file_names)
        
        try:
            # 调用MinerU的do_parse函数
            do_parse(
                output_dir=output_dir,
                pdf_file_names=file_names,
                pdf_bytes_list=file_bytes_list,
                p_lang_list=lang_list,
                backend=config["backend"],
                parse_method=config["parse_method"],
                formula_enable=config["formula_enable"],
                table_enable=config["table_enable"],
                server_url=config["server_url"],
                f_draw_layout_bbox=False,
                f_draw_span_bbox=False,
                f_dump_md=config["return_md"],
                f_dump_middle_json=config["return_middle_json"],
                f_dump_model_output=config["return_model_output"],
                f_dump_orig_pdf=False,
                f_dump_content_list=config["return_content_list"],
                start_page_id=config["start_page_id"],
                end_page_id=config["end_page_id"],
            )
            
            # 收集结果
            return self._collect_results(output_dir, file_names, config)
            
        except Exception as e:
            logger.exception(f"MinerU处理失败: {str(e)}")
            raise
    
    def _collect_results(self, output_dir: str, file_names: List[str], config: Dict) -> Dict[str, Any]:
        """收集处理结果"""
        results = {}
        
        for file_name in file_names:
            results[file_name] = {}
            
            # 确定解析结果目录
            if config["backend"].startswith("pipeline"):
                parse_dir = os.path.join(output_dir, file_name, config["parse_method"])
            else:
                parse_dir = os.path.join(output_dir, file_name, "vlm")
            
            if os.path.exists(parse_dir):
                # 读取Markdown结果
                if config["return_md"]:
                    md_file = os.path.join(parse_dir, f"{file_name}.md")
                    if os.path.exists(md_file):
                        with open(md_file, "r", encoding="utf-8") as f:
                            results[file_name]["md_content"] = f.read()
                
                # 读取其他格式结果
                if config["return_middle_json"]:
                    json_file = os.path.join(parse_dir, f"{file_name}_middle.json")
                    if os.path.exists(json_file):
                        with open(json_file, "r", encoding="utf-8") as f:
                            results[file_name]["middle_json"] = json.load(f)
                
                if config["return_model_output"]:
                    if config["backend"].startswith("pipeline"):
                        model_file = os.path.join(parse_dir, f"{file_name}_model.json")
                    else:
                        model_file = os.path.join(parse_dir, f"{file_name}_model_output.txt")
                    
                    if os.path.exists(model_file):
                        with open(model_file, "r", encoding="utf-8") as f:
                            if model_file.endswith('.json'):
                                results[file_name]["model_output"] = json.load(f)
                            else:
                                results[file_name]["model_output"] = f.read()
                
                if config["return_content_list"]:
                    content_file = os.path.join(parse_dir, f"{file_name}_content_list.json")
                    if os.path.exists(content_file):
                        with open(content_file, "r", encoding="utf-8") as f:
                            results[file_name]["content_list"] = json.load(f)
        
        return results


def parse_image_to_markdown(
    image_path: Union[str, Path],
    output_dir: str = "./output",
    model_type: str = "vlm-transformers",
    dpi: int = 300,
    **kwargs
) -> str:
    """
    解析图像文件为Markdown格式
    
    Args:
        image_path: 图像文件路径
        output_dir: 输出目录，默认"./output"
        model_type: 模型类型，默认"vlm-transformers"
        dpi: 图像分辨率，默认300
        **kwargs: 其他配置参数
        
    Returns:
        Markdown格式的解析结果
        
    Raises:
        FileNotFoundError: 文件不存在
        ValueError: 不支持的文件格式
        Exception: 处理过程中的其他错误
    """
    # 初始化解析器
    doc_parser = DocumentParser(dpi=dpi, output_dir=output_dir)
    mineru_processor = MineruProcessor(model_type=model_type, **kwargs)
    
    # 转换为Path对象
    image_path = Path(image_path)
    file_name = safe_stem(image_path.stem)
    
    # 创建唯一的输出目录
    unique_dir = os.path.join(output_dir, str(uuid.uuid4()))
    os.makedirs(unique_dir, exist_ok=True)
    
    try:
        # 加载文件字节数据
        file_bytes = doc_parser.load_file_bytes(image_path)
        
        # 处理文件
        results = mineru_processor.process_files(
            file_bytes_list=[file_bytes],
            file_names=[file_name],
            output_dir=unique_dir
        )
        
        # 返回Markdown内容
        if file_name in results and "md_content" in results[file_name]:
            return results[file_name]["md_content"]
        else:
            raise Exception("未能生成Markdown内容")
            
    except Exception as e:
        logger.error(f"图像解析失败: {str(e)}")
        raise
    

def parse_multiple_files(
    file_paths: List[Union[str, Path]],
    output_dir: str = "./output",
    model_type: str = "vlm-transformers",
    dpi: int = 300,
    **kwargs
) -> Dict[str, str]:
    """
    批量解析多个文件为Markdown格式
    
    Args:
        file_paths: 文件路径列表
        output_dir: 输出目录，默认"./output"
        model_type: 模型类型，默认"vlm-transformers"
        dpi: 图像分辨率，默认300
        **kwargs: 其他配置参数
        
    Returns:
        文件名到Markdown内容的字典
    """
    # 初始化解析器
    doc_parser = DocumentParser(dpi=dpi, output_dir=output_dir)
    mineru_processor = MineruProcessor(model_type=model_type, **kwargs)
    
    # 创建唯一的输出目录
    unique_dir = os.path.join(output_dir, str(uuid.uuid4()))
    os.makedirs(unique_dir, exist_ok=True)
    
    try:
        # 准备文件数据
        file_bytes_list = []
        file_names = []
        
        for file_path in file_paths:
            file_path = Path(file_path)
            file_name = safe_stem(file_path.stem)
            file_bytes = doc_parser.load_file_bytes(file_path)
            
            file_bytes_list.append(file_bytes)
            file_names.append(file_name)
        
        # 批量处理文件
        results = mineru_processor.process_files(
            file_bytes_list=file_bytes_list,
            file_names=file_names,
            output_dir=unique_dir
        )
        
        # 提取Markdown内容
        markdown_results = {}
        for file_name in file_names:
            if file_name in results and "md_content" in results[file_name]:
                markdown_results[file_name] = results[file_name]["md_content"]
            else:
                markdown_results[file_name] = f"# 解析失败\n\n文件 {file_name} 未能生成Markdown内容。"
        
        return markdown_results
        
    except Exception as e:
        logger.error(f"批量文件解析失败: {str(e)}")
        raise


if __name__ == "__main__":
    # 示例用法
    try:
        # 单个图像解析
        image_path = "基金交易截图/08940DC9-2B05-40EE-BB29-EE22F08EE309_4_5005_c.jpeg"
        if os.path.exists(image_path):
            markdown_content = parse_image_to_markdown(image_path)
            print("=== 单个图像解析结果 ===")
            print(markdown_content[:500] + "..." if len(markdown_content) > 500 else markdown_content)
    except Exception as e:
        print(f"示例运行失败: {str(e)}")