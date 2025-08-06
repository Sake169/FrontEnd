"""
文档解析器模块
支持PDF、Excel、JPG等多种格式文档解析，将多模态内容转换为Markdown格式输出
"""

from argparse import FileType
import uuid
import os
import sys
import tempfile
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
from loguru import logger
import json
import pandas as pd
import io
import mimetypes

# MinerU相关导入
from mineru.cli.common import do_parse, read_fn, pdf_suffixes, image_suffixes, prepare_env
import re
import fitz  # PyMuPDF


def safe_stem(file_path):
    """安全的文件名stem处理，只保留字母、数字、下划线和点"""
    stem = Path(file_path).stem
    return re.sub(r'[^\w.]', '_', stem)


def is_pdf_text_extractable(pdf_bytes: bytes) -> bool:
    """
    检测PDF文件是否包含可提取的文字
    
    Args:
        pdf_bytes: PDF文件的二进制数据
        
    Returns:
        bool: True表示可以提取文字，False表示主要是图像
    """
    try:
        # 使用PyMuPDF检测文字
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        total_chars = 0
        total_pages = len(doc)
        
        # 检查前几页的文字内容
        check_pages = min(3, total_pages)  # 只检查前3页
        
        for page_num in range(check_pages):
            page = doc[page_num]
            text = page.get_text()
            # 去除空白字符后计算字符数
            clean_text = ''.join(text.split())
            total_chars += len(clean_text)
        
        doc.close()
        
        # 如果平均每页有超过100个字符，认为是文字PDF
        avg_chars_per_page = total_chars / check_pages if check_pages > 0 else 0
        is_text_pdf = avg_chars_per_page > 100
        
        logger.info(f"PDF文字检测: 平均每页{avg_chars_per_page:.0f}个字符, 判断为{'文字PDF' if is_text_pdf else '图像PDF'}")
        return is_text_pdf
        
    except Exception as e:
        logger.error(f"PDF文字检测失败: {str(e)}")
        return False  # 检测失败时默认使用图像处理


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    从PDF中提取文字内容
    
    Args:
        pdf_bytes: PDF文件的二进制数据
        
    Returns:
        str: 提取的文字内容
    """
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        full_text = ""
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            full_text += f"\n--- 第{page_num + 1}页 ---\n"
            full_text += text
        
        doc.close()
        
        logger.info(f"成功提取PDF文字，共{len(full_text)}个字符")
        return full_text.strip()
        
    except Exception as e:
        logger.error(f"PDF文字提取失败: {str(e)}")
        return ""


def check_extraction_quality(extracted_data: dict) -> bool:
    """
    检查提取数据的质量
    
    Args:
        extracted_data: 提取的结构化数据
        
    Returns:
        bool: True表示质量良好，False表示需要二次解析
    """
    try:
        # 如果数据为空或格式不正确，认为质量不佳
        if not extracted_data or 'files' not in extracted_data:
            logger.info("数据质量检查: 数据为空或格式错误，质量不佳")
            return False
        
        total_records = 0
        valid_records = 0
        
        # 遍历所有文件和记录
        for file_data in extracted_data.get('files', []):
            for record in file_data.get('records', []):
                total_records += 1
                data = record.get('data', {})
                
                # 检查必需的三个字段
                # 1. 产品代码或产品名称或企业名称
                product_code = data.get('产品代码', '').strip()
                product_name = data.get('产品名称', '').strip()
                enterprise_name = data.get('企业名称', '').strip()

                has_product_info = bool(product_code) or bool(product_name) or bool(enterprise_name)
                
                # 2. 日期信息（交易日期或持仓日期或成交日期）
                trade_date = data.get('交易日期', '').strip()
                trade_1_date = data.get('持仓日期', '').strip()
                trade_2_date = data.get('成交日期', '').strip()
                has_date_info = bool(trade_date) or bool(trade_1_date) or bool(trade_2_date)
                
                # 3. 交易份额或交易金额或持仓份额
                trade_amount = data.get('交易份额', None)
                trade_money = data.get('交易金额', None)
                position_amount = data.get('持仓份额', None)
                has_amount_info = (trade_amount is not None and trade_amount != '') or \
                                 (trade_money is not None and trade_money != '') or \
                                 (position_amount is not None and position_amount != '')
                
                # 如果三个必需字段都有值，则该记录质量良好
                if has_product_info and has_date_info and has_amount_info:
                    valid_records += 1
                    logger.debug(f"记录质量良好: 产品={product_name or product_code}, "
                               f"日期={trade_date or trade_1_date or trade_2_date}, 份额/金额={trade_amount or trade_money or position_amount}")
                else:
                    logger.info(f"记录质量不佳: 产品信息={'有' if has_product_info else '无'}, "
                              f"日期信息={'有' if has_date_info else '无'}, "
                              f"份额/金额信息={'有' if has_amount_info else '无'}")
        
        # 只有所有记录都符合要求才认为质量良好
        quality_good = (total_records > 0) and (valid_records == total_records)
        
        logger.info(f"数据质量检查: 总记录数={total_records}, 有效记录数={valid_records}, "
                   f"质量={'良好' if quality_good else '需要改进'}")
        
        return quality_good
        
    except Exception as e:
        logger.error(f"数据质量检查失败: {str(e)}")
        return True  # 检查失败时默认认为质量良好


def detect_file_type(file_bytes: bytes, file_name: str = "") -> str:
    """
    检测文件类型
    
    Args:
        file_bytes: 文件二进制数据
        file_name: 文件名（可选，用于辅助检测）
        
    Returns:
        文件类型字符串：'pdf', 'jpg', 'xlsx', 'unknown'
    """
    try:
        # 首先尝试通过文件名检测
        if file_name:
            file_ext = Path(file_name).suffix.lower()
            if file_ext in ['.pdf']:
                return 'pdf'
            elif file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.gif', '.webp']:
                return 'jpg'
            elif file_ext in ['.xlsx', '.xls']:
                return 'xlsx'
        
        # 通过文件头检测
        if len(file_bytes) >= 4:
            # PDF文件头检测
            if file_bytes[:4] == b'%PDF':
                return 'pdf'
            
            # Excel文件头检测
            if file_bytes[:4] == b'PK\x03\x04':  # ZIP格式（Excel文件是ZIP格式）
                # 进一步检查是否为Excel
                try:
                    import zipfile
                    with io.BytesIO(file_bytes) as bio:
                        with zipfile.ZipFile(bio) as zf:
                            if any(name.startswith('xl/') for name in zf.namelist()):
                                return 'excel'
                except:
                    pass
            
            # 图像文件头检测
            image_signatures = {
                b'\xff\xd8\xff': 'jpg',  # JPEG
                b'\x89PNG\r\n\x1a\n': 'jpg',  # PNG
                b'GIF87a': 'jpg',  # GIF
                b'GIF89a': 'jpg',  # GIF
                b'BM': 'jpg',  # BMP
                b'II*\x00': 'jpg',  # TIFF (little endian)
                b'MM\x00*': 'jpg',  # TIFF (big endian)
            }
            
            for signature, file_type in image_signatures.items():
                if file_bytes.startswith(signature):
                    return file_type
        
        logger.warning(f"无法检测文件类型，文件名: {file_name}")
        return 'unknown'
        
    except Exception as e:
        logger.error(f"文件类型检测失败: {str(e)}")
        return 'unknown'


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
            logger.info(f"开始使用MinerU处理 {len(file_names)} 个文件")
            
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
            
            logger.info("MinerU处理完成，开始收集结果")
            
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
                        logger.info(f"成功读取Markdown文件: {md_file}")
                    else:
                        logger.warning(f"Markdown文件不存在: {md_file}")
                
                # 读取其他格式结果（可选）
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
            else:
                logger.error(f"解析目录不存在: {parse_dir}")
        
        return results


def excel_to_markdown(excel_bytes: bytes) -> str:
    """
    将Excel文件转换为HTML表格格式
    
    Args:
        excel_bytes: Excel文件的二进制数据
        
    Returns:
        HTML表格格式的字符串
        
    Raises:
        ValueError: 无效的输入数据
        Exception: 处理过程中的其他错误
    """
    try:
        logger.info("开始处理Excel文件")
        
        # 读取Excel文件
        excel = pd.read_excel(io.BytesIO(excel_bytes))
        
        logger.info(f"Excel文件读取成功，包含 {len(excel)} 行数据，{len(excel.columns)} 列")
        
        # 处理列名，将NaN列名替换为有意义的名字
        columns = []
        for i, col in enumerate(excel.columns):
            if pd.isna(col) or str(col).startswith('Unnamed:'):
                columns.append(f"列{i+1}")
            else:
                columns.append(str(col))
        
        # 开始构建HTML表格
        html_parts = ['<table>']
        
        # 添加表头行
        html_parts.append('<tr>')
        for col in columns:
            html_parts.append(f'<td>{col}</td>')
        html_parts.append('</tr>')
        
        # 获取表格主体
        excel_table_body = list(excel.iloc[0:].values)
        
        # 将每一个列表项转换为HTML行
        for row in excel_table_body:
            html_parts.append('<tr>')
            for cell in row:
                # 处理NaN值
                if pd.isna(cell):
                    html_parts.append('<td></td>')
                else:
                    # 转义HTML特殊字符
                    cell_str = str(cell)
                    cell_str = cell_str.replace('&', '&amp;')
                    cell_str = cell_str.replace('<', '&lt;')
                    cell_str = cell_str.replace('>', '&gt;')
                    cell_str = cell_str.replace('"', '&quot;')
                    cell_str = cell_str.replace("'", '&#39;')
                    html_parts.append(f'<td>{cell_str}</td>')
            html_parts.append('</tr>')
        
        # 结束HTML表格
        html_parts.append('</table>')
        
        # 拼接成完整的HTML表格
        html_table = ''.join(html_parts)
        
        logger.info("Excel转HTML表格完成")
        return html_table
        
    except Exception as e:
        logger.error(f"Excel转HTML表格失败: {str(e)}")
        raise


def parse_document_from_bytes(
    file_bytes: bytes,
    file_name: str = "document",
    file_type: Optional[str] = None,
    output_dir: str = "./output",
    model_type: str = "vlm-transformers",
    **kwargs
) -> str:
    """
    主函数：从二进制文件流解析文档为Markdown格式
    
    Args:
        file_bytes: 文件的二进制数据
        file_name: 文件名，用于输出文件命名
        file_type: 文件类型（可选，如果不提供会自动检测）
        output_dir: 输出目录，默认"./output"
        model_type: 模型类型，默认"vlm-transformers"
        **kwargs: 其他配置参数
        
    Returns:
        Markdown格式的解析结果
        
    Raises:
        ValueError: 无效的输入数据
        Exception: 处理过程中的其他错误
    """
    if not file_bytes:
        raise ValueError("文件二进制数据不能为空")
    
    logger.info(f"开始解析文档: {file_name}")
    logger.info(f"文件大小: {len(file_bytes)} bytes")
    
    # 检测文件类型
    if file_type is None:
        file_type = detect_file_type(file_bytes, file_name)
        logger.info(f"检测到文件类型: {file_type}")
    
    # 安全的文件名处理
    safe_file_name = safe_stem(file_name)
    
    try:
        if file_type in ['pdf', 'jpg']:
            # 处理PDF文件
            if file_type == 'pdf':
                # 检查PDF是否包含可提取的文字
                if is_pdf_text_extractable(file_bytes):
                    logger.info("PDF包含可提取文字，使用文字提取方案")
                    markdown = extract_text_from_pdf(file_bytes)
                else:
                    logger.info("PDF主要为图像，使用MinerU处理")
                    # 使用MinerU处理图像PDF
                    mineru_processor = MineruProcessor(model_type=model_type, **kwargs)
                    unique_dir = os.path.join(output_dir, str(uuid.uuid4()))
                    os.makedirs(unique_dir, exist_ok=True)
                    
                    results = mineru_processor.process_files(
                        file_bytes_list=[file_bytes],
                        file_names=[safe_file_name],
                        output_dir=unique_dir
                    )
                    
                    if safe_file_name in results and "md_content" in results[safe_file_name]:
                        markdown = results[safe_file_name]["md_content"]
                    else:
                        raise Exception("MinerU未能生成Markdown内容")
            
            # 处理图像文件
            elif file_type == 'jpg':
                logger.info("图像文件，使用MinerU处理")
                from mineru.utils.pdf_image_tools import images_bytes_to_pdf_bytes
                # 保存原始图像字节数据用于可能的二次解析
                original_image_bytes = file_bytes
                file_bytes = images_bytes_to_pdf_bytes(file_bytes)
                
                mineru_processor = MineruProcessor(model_type=model_type, **kwargs)
                unique_dir = os.path.join(output_dir, str(uuid.uuid4()))
                os.makedirs(unique_dir, exist_ok=True)
                
                results = mineru_processor.process_files(
                    file_bytes_list=[file_bytes],
                    file_names=[safe_file_name],
                    output_dir=unique_dir
                )
                
                if safe_file_name in results and "md_content" in results[safe_file_name]:
                    markdown = results[safe_file_name]["md_content"]
                else:
                    raise Exception("MinerU未能生成Markdown内容")
                
        elif file_type == 'xlsx':
            # 使用Excel转HTML表格处理
            logger.info("使用Excel转HTML表格处理")
            markdown = excel_to_markdown(file_bytes)
            
        else:
            raise ValueError(f"不支持的文件类型: {file_type}")
            
    except Exception as e:
        logger.error(f"文档解析失败: {str(e)}")
        raise
    # 保存md文件到output目录
    with open(f'{output_dir}/{safe_file_name}.md', 'w', encoding='utf-8') as f:
        f.write(markdown)
    logger.info(f"Markdown文件已保存到: {output_dir}/{safe_file_name}.md")
    
    # 返回结果
    result = {'text_list': [
        {
            'file_type': f'{file_type}',
            'file_text': markdown
        }
     ]}
    
    # 如果指定了模板路径，则进行进一步处理
    template_path = kwargs.get('template_path')
    if template_path and Path(template_path).exists():
        try:
            # 导入并调用main.py的处理函数
            sys.path.append('/Users/jackliu/AI_Services/ai_manage/AiInvestmentFilingPlatform/backend-service/models/qwen-api-framework')
            from extactor import process_document_parsing_result
            
            # 处理文档解析结果
            processing_result = process_document_parsing_result(
                result, 
                Path(output_dir), 
                Path(template_path)
            )
            
            # 检查提取数据的质量
            if processing_result.get('success') and 'extracted_data' in processing_result:
                extraction_quality = check_extraction_quality(processing_result['extracted_data'])
                
                # 如果质量不佳且当前使用的不是vlm-transformers，进行二次解析
                if not extraction_quality and model_type != 'vlm-transformers' and not kwargs.get('is_second_parsing', False):
                    logger.info("数据质量不佳，使用vlm-transformers进行二次解析")
                    
                    try:
                        # 重新解析文档内容
                        second_markdown = None
                        if file_type == 'pdf':
                            # 对于PDF，强制使用MinerU
                            mineru_processor = MineruProcessor(model_type='vlm-transformers', **kwargs)
                            unique_dir = os.path.join(output_dir, str(uuid.uuid4()) + "_second")
                            os.makedirs(unique_dir, exist_ok=True)
                            
                            results = mineru_processor.process_files(
                                file_bytes_list=[file_bytes],
                                file_names=[safe_file_name + "_second"],
                                output_dir=unique_dir
                            )
                            
                            if safe_file_name + "_second" in results and "md_content" in results[safe_file_name + "_second"]:
                                second_markdown = results[safe_file_name + "_second"]["md_content"]
                        
                        elif file_type == 'jpg':
                            # 对于图像，使用vlm-transformers模式的MinerU
                            from mineru.utils.pdf_image_tools import images_bytes_to_pdf_bytes
                            # 使用保存的原始图像字节数据
                            if 'original_image_bytes' in locals():
                                image_pdf_bytes = images_bytes_to_pdf_bytes(original_image_bytes)
                                
                                mineru_processor = MineruProcessor(model_type='vlm-transformers', **kwargs)
                                unique_dir = os.path.join(output_dir, str(uuid.uuid4()) + "_second")
                                os.makedirs(unique_dir, exist_ok=True)
                                
                                results = mineru_processor.process_files(
                                    file_bytes_list=[image_pdf_bytes],
                                    file_names=[safe_file_name + "_second"],
                                    output_dir=unique_dir
                                )
                                
                                if safe_file_name + "_second" in results and "md_content" in results[safe_file_name + "_second"]:
                                    second_markdown = results[safe_file_name + "_second"]["md_content"]
                            else:
                                # 如果没有保存原始数据，跳过二次解析
                                logger.warning("未找到原始图像数据，跳过二次解析")
                                second_markdown = None
                        
                        # 如果成功获取二次解析的内容，重新处理
                        if second_markdown:
                            second_result = {'text_list': [{'file_type': file_type, 'file_text': second_markdown}]}
                            
                            # 重新提取数据
                            second_processing_result = process_document_parsing_result(
                                second_result, 
                                Path(output_dir), 
                                Path(template_path)
                            )
                            
                            # 检查二次解析的质量
                            if second_processing_result.get('success'):
                                logger.info("二次解析成功，质量改善")
                                result['text_list'][0]['file_text'] = second_markdown
                                result['processing_result'] = second_processing_result
                                result['second_parsing'] = True
                            else:
                                logger.warning("二次解析处理失败，使用原始结果")
                                result['processing_result'] = processing_result
                                result['second_parsing_failed'] = True
                        else:
                            logger.warning("二次解析未产生内容，使用原始结果")
                            result['processing_result'] = processing_result
                            result['second_parsing_no_content'] = True
                            
                    except Exception as e:
                        logger.error(f"二次解析失败: {str(e)}")
                        result['processing_result'] = processing_result
                        result['second_parsing_error'] = str(e)
                else:
                    # 质量良好或已经是vlm-transformers，使用当前结果
                    result['processing_result'] = processing_result
            else:
                result['processing_result'] = processing_result
            
        except Exception as e:
            logger.warning(f"进一步处理失败: {str(e)}")
            result['processing_error'] = str(e)
    
    return result


if __name__ == "__main__":
    """
    测试文档解析功能
    """
    # file_path = "./test/基金E账户App投资者公募基金持有信息-【2025-02-26】.xlsx"
    # file_path = "/Users/jackliu/Downloads/基金交易截图/F66D2E4D-578B-4537-930B-5CA18583A079_4_5005_c.jpeg"
    file_path = "/Users/jackliu/AI_Services/ai_manage/AiInvestmentFilingPlatform/test/证券查询业务_在线_1311657086082001（无持仓）-封基.pdf"

    file_path = Path(file_path)
    
    # 读取文件二进制数据
    with open(file_path, 'rb') as f:
        file_bytes = f.read()

    result = parse_document_from_bytes(
        file_bytes=file_bytes,
        file_name=file_path.name,
        output_dir='/Users/jackliu/AI_Services/ai_manage/AiInvestmentFilingPlatform/output',
        model_type='pipeline'
    )
