from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from typing import Optional, Dict, Any
import json

from ..core.dependencies import get_logger
from ..services.ai_service import AIService
from pydantic import BaseModel

router = APIRouter(prefix="/ai", tags=["AI服务"])

# 依赖注入
ai_service = AIService()

class AIProcessRequest(BaseModel):
    """AI处理请求模型"""
    file_path: str
    content_type: str
    options: Optional[Dict[str, Any]] = None

class AIProcessResponse(BaseModel):
    """AI处理响应模型"""
    success: bool
    message: str
    result: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = None
    processing_time: Optional[float] = None

class AIModelInfo(BaseModel):
    """AI模型信息"""
    model_name: str
    version: str
    description: str
    supported_formats: list
    capabilities: list

@router.post("/process", response_model=AIProcessResponse, summary="AI文件处理")
async def process_file_with_ai(
    request: AIProcessRequest,
    logger = Depends(get_logger)
):
    """
    使用AI模型处理文件
    
    - **file_path**: 文件路径
    - **content_type**: 文件类型
    - **options**: 处理选项
    """
    try:
        logger.info(f"开始AI处理文件: {request.file_path}")
        
        # 调用AI服务处理文件
        result = await ai_service.process_file(
            file_path=request.file_path,
            content_type=request.content_type,
            options=request.options
        )
        
        response = AIProcessResponse(
            success=True,
            message="AI处理完成",
            result=result.get('data'),
            confidence=result.get('confidence'),
            processing_time=result.get('processing_time')
        )
        
        logger.info(f"AI处理完成: {request.file_path}")
        
        return response
        
    except Exception as e:
        logger.error(f"AI处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI处理失败: {str(e)}")

@router.post("/extract-text", summary="提取文本内容")
async def extract_text_from_file(
    file: UploadFile = File(...),
    logger = Depends(get_logger)
):
    """
    从图片或PDF文件中提取文本内容
    
    - **file**: 上传的文件
    """
    try:
        logger.info(f"开始提取文本: {file.filename}")
        
        # 读取文件内容
        file_content = await file.read()
        
        # 调用AI服务提取文本
        text_result = await ai_service.extract_text(
            file_content=file_content,
            content_type=file.content_type,
            filename=file.filename
        )
        
        logger.info(f"文本提取完成: {file.filename}")
        
        return {
            "success": True,
            "message": "文本提取成功",
            "text": text_result.get('text', ''),
            "confidence": text_result.get('confidence', 0.0),
            "language": text_result.get('language', 'unknown')
        }
        
    except Exception as e:
        logger.error(f"文本提取失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"文本提取失败: {str(e)}")

@router.post("/analyze-document", summary="分析文档结构")
async def analyze_document_structure(
    file: UploadFile = File(...),
    analysis_type: str = "securities_trading",
    logger = Depends(get_logger)
):
    """
    分析文档结构并提取结构化数据
    
    - **file**: 上传的文件
    - **analysis_type**: 分析类型（securities_trading: 证券交易, general: 通用）
    """
    try:
        logger.info(f"开始分析文档: {file.filename}, 类型: {analysis_type}")
        
        # 读取文件内容
        file_content = await file.read()
        
        # 调用AI服务分析文档
        analysis_result = await ai_service.analyze_document(
            file_content=file_content,
            content_type=file.content_type,
            analysis_type=analysis_type,
            filename=file.filename
        )
        
        logger.info(f"文档分析完成: {file.filename}")
        
        return {
            "success": True,
            "message": "文档分析成功",
            "structure": analysis_result.get('structure', {}),
            "extracted_data": analysis_result.get('extracted_data', []),
            "confidence": analysis_result.get('confidence', 0.0),
            "suggestions": analysis_result.get('suggestions', [])
        }
        
    except Exception as e:
        logger.error(f"文档分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"文档分析失败: {str(e)}")

@router.get("/models", response_model=list[AIModelInfo], summary="获取可用AI模型")
async def get_available_models(
    logger = Depends(get_logger)
):
    """
    获取可用的AI模型列表
    """
    try:
        models = await ai_service.get_available_models()
        
        logger.info(f"返回 {len(models)} 个可用模型")
        
        return models
        
    except Exception as e:
        logger.error(f"获取模型列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取模型列表失败")

@router.get("/health", summary="AI服务健康检查")
async def ai_service_health(
    logger = Depends(get_logger)
):
    """
    检查AI服务的健康状态
    """
    try:
        health_status = await ai_service.health_check()
        
        return {
            "status": "healthy" if health_status.get('available', False) else "unhealthy",
            "models_available": health_status.get('models_count', 0),
            "last_check": health_status.get('last_check'),
            "response_time": health_status.get('response_time'),
            "details": health_status.get('details', {})
        }
        
    except Exception as e:
        logger.error(f"AI服务健康检查失败: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@router.post("/configure", summary="配置AI服务")
async def configure_ai_service(
    config: Dict[str, Any],
    logger = Depends(get_logger)
):
    """
    配置AI服务参数
    
    - **config**: 配置参数字典
    """
    try:
        logger.info(f"配置AI服务: {config}")
        
        result = await ai_service.configure(config)
        
        return {
            "success": True,
            "message": "AI服务配置成功",
            "applied_config": result.get('applied_config', {}),
            "restart_required": result.get('restart_required', False)
        }
        
    except Exception as e:
        logger.error(f"配置AI服务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"配置失败: {str(e)}")