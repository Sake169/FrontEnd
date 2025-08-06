from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
import json
import uuid
from datetime import datetime
from pathlib import Path
import aiofiles
from typing import Optional

from ..models.upload import RelatedPersonInfo, UploadResponse, UploadStatus, FileInfo
from ..core.dependencies import get_logger, validate_file_size, validate_file_type, get_upload_path
from ..services.file_service import FileService
from ..services.ai_service import AIService
from ..services.excel_service import ExcelService

router = APIRouter(tags=["文件上传"], include_in_schema=True)

# 依赖注入
file_service = FileService()
ai_service = AIService()
excel_service = ExcelService()

@router.post("/upload", response_model=UploadResponse, summary="上传文件并处理")
async def upload_file(
    file: UploadFile = File(..., description="上传的文件（图片或PDF）"),
    relatedPersonInfo: str = Form(..., description="相关人员信息JSON字符串"),
    upload_path: str = Depends(get_upload_path),
    logger = Depends(get_logger)
):
    """
    上传文件并进行AI识别处理
    
    - **file**: 支持的文件类型：JPEG, PNG, GIF, WebP, PDF
    - **related_person_info**: 相关人员信息，JSON格式
    
    返回处理结果和生成的Excel文件信息
    """
    upload_id = str(uuid.uuid4())
    
    try:
        # 解析相关人员信息
        try:
            person_data = json.loads(relatedPersonInfo)
            person_info = RelatedPersonInfo(**person_data)
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"解析相关人员信息失败: {e}")
            raise HTTPException(status_code=400, detail="相关人员信息格式错误")
        
        # 验证文件
        if not file.filename:
            raise HTTPException(status_code=400, detail="文件名不能为空")
        
        # 读取文件内容以获取大小
        file_content = await file.read()
        file_size = len(file_content)
        
        # 验证文件大小
        if not validate_file_size(file_size):
            raise HTTPException(status_code=400, detail="文件大小超过限制")
        
        # 验证文件类型
        if not validate_file_type(file.content_type or ""):
            raise HTTPException(status_code=400, detail="不支持的文件类型")
        
        logger.info(f"开始处理上传文件: {file.filename}, 大小: {file_size} bytes")
        
        # 保存文件
        file_path = await file_service.save_uploaded_file(
            file_content, file.filename, upload_path
        )
        
        logger.info(f"文件已保存: {file_path}")
        
        # AI识别处理（异步）
        try:
            ai_result = await ai_service.process_file(file_path, file.content_type)
            logger.info(f"AI识别完成: {ai_result}")
        except Exception as e:
            logger.warning(f"AI识别失败，使用默认数据: {e}")
            ai_result = None
        
        # 生成Excel文件
        excel_filename = f"processed_{upload_id}.xlsx"
        
        # 准备Excel数据
        excel_data = [
            {
                "姓名": person_info.name,
                "关系": person_info.relationship,
                "身份证号": person_info.id_number,
                "电话": person_info.phone,
                "处理时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "文件名": file.filename,
                "AI识别结果": str(ai_result) if ai_result else "无"
            }
        ]
        
        excel_path = await excel_service.save_excel_data(
            data=excel_data,
            filename=excel_filename,
            sheet_name="人员信息"
        )
        
        logger.info(f"Excel文件已生成: {excel_path}")
        
        # 构建响应
        response = UploadResponse(
            success=True,
            message=f"文件上传成功，已为{person_info.name}生成Excel报表",
            excel_url=f"/download/{excel_filename}",
            file_name=excel_filename,
            upload_id=upload_id,
            created_at=datetime.now()
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"处理文件时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理文件时出错: {str(e)}")

@router.get("/status/{upload_id}", response_model=UploadStatus, summary="查询上传状态")
async def get_upload_status(
    upload_id: str,
    logger = Depends(get_logger)
):
    """
    查询文件上传和处理状态
    
    - **upload_id**: 上传ID
    """
    try:
        # 这里可以从数据库或缓存中查询状态
        # 目前返回模拟数据
        status = UploadStatus(
            upload_id=upload_id,
            status="completed",
            progress=100,
            message="处理完成"
        )
        
        return status
        
    except Exception as e:
        logger.error(f"查询上传状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail="查询状态失败")

@router.get("/history", summary="获取上传历史")
async def get_upload_history(
    limit: int = 10,
    offset: int = 0,
    logger = Depends(get_logger)
):
    """
    获取文件上传历史记录
    
    - **limit**: 返回记录数量限制
    - **offset**: 偏移量
    """
    try:
        # 这里可以从数据库查询历史记录
        # 目前返回空列表
        return {
            "history": [],
            "total": 0,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"获取上传历史失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取历史记录失败")