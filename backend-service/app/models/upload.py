from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class RelatedPersonInfo(BaseModel):
    """相关人员信息模型"""
    name: str = Field(..., description="姓名", min_length=1, max_length=50)
    relationship: str = Field(..., description="关系", min_length=1, max_length=20)
    id_number: str = Field(..., description="身份证号", min_length=15, max_length=18, alias="idNumber")
    phone: str = Field(..., description="电话号码", min_length=11, max_length=15)
    description: Optional[str] = Field(None, description="备注", max_length=200)
    
    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "name": "张三",
                "relationship": "配偶",
                "idNumber": "110101199001011234",
                "phone": "13800138000",
                "description": "备注信息"
            }
        }

class UploadResponse(BaseModel):
    """文件上传响应模型"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    excel_url: Optional[str] = Field(None, description="Excel文件URL", alias="excelUrl")
    file_name: Optional[str] = Field(None, description="文件名", alias="fileName")
    upload_id: Optional[str] = Field(None, description="上传ID", alias="uploadId")
    created_at: Optional[datetime] = Field(None, description="创建时间", alias="createdAt")
    
    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "success": True,
                "message": "文件上传成功",
                "excelUrl": "/download/processed_result.xlsx",
                "fileName": "processed_result.xlsx",
                "uploadId": "uuid-string",
                "createdAt": "2024-01-01T00:00:00Z"
            }
        }

class FileInfo(BaseModel):
    """文件信息模型"""
    name: str = Field(..., description="文件名")
    size: int = Field(..., description="文件大小（字节）")
    content_type: str = Field(..., description="文件类型", alias="contentType")
    upload_time: datetime = Field(..., description="上传时间", alias="uploadTime")
    
    class Config:
        allow_population_by_field_name = True

class UploadStatus(BaseModel):
    """上传状态模型"""
    upload_id: str = Field(..., description="上传ID", alias="uploadId")
    status: str = Field(..., description="状态：pending, processing, completed, failed")
    progress: int = Field(0, description="进度百分比", ge=0, le=100)
    message: str = Field("", description="状态消息")
    result: Optional[UploadResponse] = Field(None, description="处理结果")
    
    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "uploadId": "uuid-string",
                "status": "completed",
                "progress": 100,
                "message": "处理完成",
                "result": {
                    "success": True,
                    "message": "文件处理成功",
                    "excelUrl": "/download/result.xlsx",
                    "fileName": "result.xlsx"
                }
            }
        }