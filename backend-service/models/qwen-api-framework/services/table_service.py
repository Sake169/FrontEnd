import json
from typing import Dict
from pathlib import Path
import logging
from openpyxl import load_workbook
from openpyxl.styles import Font, Alignment, PatternFill
from core.client import QwenClient
from services.prompt_templates import PromptTemplates

# 初始化logger
logger = logging.getLogger(__name__)

class TableExtractionService:
    RECORD_TYPES = [
        "证券投资报备交易信息",
        "证券投资报备持仓信息",
        "场外基金报备交易信息",
        "场外基金报备持仓信息",
        "未上市股权报备交易信息",
        "未上市股权报备持仓信息"
    ]

    # 各类型字段映射表（确保与Excel模板列名一致）
    FIELD_MAPPING = {
        "证券投资报备交易信息": {
            "证券账号": "证券账号",
            "交易市场": "交易市场",
            "证券代码": "证券代码",
            "证券名称": "证券名称",
            "买卖方向": "买卖方向",
            "交易类型": "交易类型",
            "交易数量（股）": "交易数量（股）",
            "交易价格": "交易价格",
            "产品名称": "产品名称",
            "成交日期": "成交日期",
            "备注": "备注"
        },
        "证券投资报备持仓信息": {
            "证券账号": "证券账号",
            "交易市场": "交易市场",
            "证券代码": "证券代码",
            "证券名称": "证券名称",
            "持仓数量（股）": "持仓数量（股）",
            "持仓日期": "持仓日期",
            "是否零申报": "是否零申报",
            "备注": "备注"
        },
        "场外基金报备交易信息": {
            "产品代码": "产品代码",
            "产品名称": "产品名称",
            "买卖方向": "买卖方向",
            "场外基金投向": "场外基金投向",
            "交易份额": "交易份额",
            "交易日期": "交易日期",
            "是否零申报": "是否零申报",
            "备注": "备注"
        },
        "场外基金报备持仓信息": {
            "产品代码": "产品代码",
            "产品名称": "产品名称",
            "持仓份额": "持仓份额",
            "持仓日期": "持仓日期",
            "是否零申报": "是否零申报",
            "备注": "备注"
        },
        "未上市股权报备交易信息": {
            "企业名称": "企业名称",
            "统一社会信用代码": "统一社会信用代码",
            "交易方向": "交易方向",
            "认缴金额（万元）": "认缴金额（万元）",
            "实缴金额（万元）": "实缴金额（万元）",
            "持股比例（%）": "持股比例（%）",
            "交易日期": "交易日期",
            "是否零申报": "是否零申报",
            "备注": "备注",
         },
         "未上市股权报备持仓信息": {
            "企业名称": "企业名称",
            "统一社会信用代码": "统一社会信用代码",
            "交易方向": "交易方向",
            "认缴金额（万元）": "认缴金额（万元）",
            "实缴金额（万元）": "实缴金额（万元）",
            "持股比例（%）": "持股比例（%）",
            "持仓日期": "持仓日期",
            "是否零申报": "是否零申报",
            "备注": "备注",
         }
    }
    def __init__(self):
        self.client = QwenClient()
    
    def extract_typed_records(self, combined_md: str) -> Dict:
        """提取带类型识别的结构化数据"""
        prompt = PromptTemplates.get_typed_extraction_prompt(combined_md)
        
        response = self.client.chat_completion(
            messages=[{"role": "user", "content": prompt.content}],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        content = response['choices'][0]['message']['content']
        return self._validate_response(content)
    
    def _validate_response(self, content: str) -> Dict:
        """验证并解析响应"""
        try:
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0]
            
            data = json.loads(content)
            self._check_record_types(data)
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {str(e)}\n原始内容: {content[:200]}...")
            raise
        except Exception as e:
            logger.error(f"验证响应时发生错误: {str(e)}")
            raise
    
    def _check_record_types(self, data: Dict):
        """验证记录类型是否合法"""
        for file_data in data.get("files", []):
            for record in file_data.get("records", []):
                if record.get("record_type") not in self.RECORD_TYPES:
                    error_msg = f"非法记录类型: {record.get('record_type')}"
                    logger.error(error_msg)
                    raise ValueError(error_msg)

    def write_to_excel_template(self, data: Dict, template_path: Path, output_path: Path) -> bool:
        """将数据写入已有Excel模板"""
        try:
            logger.info(f"开始写入Excel模板: {template_path}")
            
            # 加载模板文件
            wb = load_workbook(template_path)
            
            # 处理每种记录类型
            for file_data in data.get("files", []):
                for record in file_data.get("records", []):
                    record_type = record["record_type"]
                    if record_type not in wb.sheetnames:
                        logger.warning(f"模板中缺少对应的工作表: {record_type}")
                        continue
                    
                    sheet = wb[record_type]
                    # 找到第一个空行
                    row = sheet.max_row + 1
                    
                    # 获取字段映射关系
                    field_map = self.FIELD_MAPPING.get(record_type, {})
                    
                    # 写入数据
                    for col in range(1, sheet.max_column + 1):
                        header = sheet.cell(row=1, column=col).value
                        if header in field_map:
                            json_key = field_map[header]
                            value = record["data"].get(json_key, "")
                            sheet.cell(row=row, column=col, value=value)
            
            # 保存新文件
            wb.save(output_path)
            logger.info(f"成功保存Excel文件: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"写入Excel模板失败: {str(e)}", exc_info=True)
            raise ValueError(f"写入Excel模板失败: {str(e)}")