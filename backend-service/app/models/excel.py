from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime

class SaveExcelRequest(BaseModel):
    """保存Excel请求模型"""
    file_name: str = Field(..., description="文件名", alias="fileName")
    data: List[List[Any]] = Field(..., description="Excel数据（二维数组）")
    sheets: Optional[List[str]] = Field(None, description="工作表名称列表")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "fileName": "report.xlsx",
                "data": [
                    ["姓名", "部门", "职位"],
                    ["张三", "技术部", "工程师"],
                    ["李四", "销售部", "经理"]
                ],
                "sheets": ["Sheet1"]
            }
        }

class SaveExcelResponse(BaseModel):
    """保存Excel响应模型"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    file_path: Optional[str] = Field(None, description="文件路径", alias="filePath")
    download_url: Optional[str] = Field(None, description="下载URL", alias="downloadUrl")
    
    class Config:
        populate_by_name = True

class ExcelFileInfo(BaseModel):
    """Excel文件信息模型"""
    name: str = Field(..., description="文件名")
    size: int = Field(..., description="文件大小（字节）")
    modified: datetime = Field(..., description="修改时间")
    sheets: List[str] = Field([], description="工作表名称列表")
    rows: int = Field(0, description="行数")
    columns: int = Field(0, description="列数")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "report.xlsx",
                "size": 1024,
                "modified": "2024-01-01T00:00:00Z",
                "sheets": ["Sheet1", "Sheet2"],
                "rows": 100,
                "columns": 10
            }
        }

class ExcelData(BaseModel):
    """Excel数据模型"""
    headers: List[str] = Field(..., description="列标题")
    rows: List[List[Any]] = Field(..., description="数据行")
    sheet_name: str = Field("Sheet1", description="工作表名称", alias="sheetName")
    total_rows: int = Field(..., description="总行数", alias="totalRows")
    total_columns: int = Field(..., description="总列数", alias="totalColumns")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "headers": ["姓名", "部门", "职位"],
                "rows": [
                    ["张三", "技术部", "工程师"],
                    ["李四", "销售部", "经理"]
                ],
                "sheetName": "Sheet1",
                "totalRows": 2,
                "totalColumns": 3
            }
        }

class ExcelTemplate(BaseModel):
    """Excel模板模型"""
    template_name: str = Field(..., description="模板名称", alias="templateName")
    description: str = Field("", description="模板描述")
    headers: List[str] = Field(..., description="列标题")
    default_data: List[List[Any]] = Field([], description="默认数据", alias="defaultData")
    validation_rules: Dict[str, Any] = Field({}, description="验证规则", alias="validationRules")
    
    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "templateName": "员工信息模板",
                "description": "用于录入员工基本信息",
                "headers": ["姓名", "部门", "职位", "入职日期"],
                "defaultData": [],
                "validationRules": {
                    "姓名": {"required": True, "maxLength": 50},
                    "部门": {"required": True},
                    "入职日期": {"type": "date"}
                }
            }
        }

class FileListResponse(BaseModel):
    """文件列表响应模型"""
    files: List[ExcelFileInfo] = Field(..., description="文件列表")
    total: int = Field(..., description="文件总数")
    
    class Config:
        json_schema_extra = {
            "example": {
                "files": [
                    {
                        "name": "report1.xlsx",
                        "size": 1024,
                        "modified": "2024-01-01T00:00:00Z",
                        "sheets": ["Sheet1"],
                        "rows": 100,
                        "columns": 5
                    }
                ],
                "total": 1
            }
        }