from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from pathlib import Path
from typing import List
import os
from datetime import datetime

from ..models.excel import (
    SaveExcelRequest, SaveExcelResponse, ExcelFileInfo, 
    ExcelData, FileListResponse, ExcelTemplate
)
from ..core.dependencies import get_logger, get_output_path
from ..services.excel_service import ExcelService

router = APIRouter(prefix="/excel", tags=["Excel处理"])

# 依赖注入
excel_service = ExcelService()

@router.post("/save", response_model=SaveExcelResponse, summary="保存Excel数据")
async def save_excel_data(
    request: SaveExcelRequest,
    output_path: str = Depends(get_output_path),
    logger = Depends(get_logger)
):
    """
    保存编辑后的Excel数据
    
    - **fileName**: 文件名
    - **data**: Excel数据（二维数组）
    - **sheets**: 工作表名称列表（可选）
    """
    try:
        logger.info(f"开始保存Excel数据: {request.file_name}")
        
        # 保存Excel文件
        file_path = await excel_service.save_excel_data(
            data=request.data,
            filename=request.file_name,
            sheets=request.sheets,
            output_dir=output_path
        )
        
        logger.info(f"Excel文件已保存: {file_path}")
        
        response = SaveExcelResponse(
            success=True,
            message="Excel数据保存成功",
            file_path=str(file_path),
            download_url=f"/download/{request.file_name}"
        )
        
        return response
        
    except Exception as e:
        logger.error(f"保存Excel数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"保存数据失败: {str(e)}")

@router.get("/download/{filename}", summary="下载Excel文件")
async def download_excel_file(
    filename: str,
    output_path: str = Depends(get_output_path),
    logger = Depends(get_logger)
):
    """
    下载生成的Excel文件
    
    - **filename**: 文件名
    """
    try:
        file_path = Path(output_path) / filename
        
        # 检查文件是否存在
        if not file_path.exists():
            # 尝试从其他位置查找文件
            alternative_paths = [
                Path("../example.xlsx"),
                Path("example.xlsx"),
                Path("outputs") / filename
            ]
            
            for alt_path in alternative_paths:
                if alt_path.exists():
                    file_path = alt_path
                    break
            else:
                logger.error(f"文件不存在: {filename}")
                raise HTTPException(status_code=404, detail="文件不存在")
        
        logger.info(f"下载文件: {file_path}")
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"下载文件失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"下载文件失败: {str(e)}")

@router.get("/files", response_model=FileListResponse, summary="获取文件列表")
async def list_excel_files(
    output_path: str = Depends(get_output_path),
    logger = Depends(get_logger)
):
    """
    列出所有可用的Excel文件
    """
    try:
        files = []
        output_dir = Path(output_path)
        
        if output_dir.exists():
            for file_path in output_dir.glob("*.xlsx"):
                try:
                    stat = file_path.stat()
                    
                    # 获取Excel文件信息
                    excel_info = await excel_service.get_excel_info(file_path)
                    
                    file_info = ExcelFileInfo(
                        name=file_path.name,
                        size=stat.st_size,
                        modified=datetime.fromtimestamp(stat.st_mtime),
                        sheets=excel_info.get('sheets', []),
                        rows=excel_info.get('rows', 0),
                        columns=excel_info.get('columns', 0)
                    )
                    
                    files.append(file_info)
                    
                except Exception as e:
                    logger.warning(f"获取文件信息失败 {file_path.name}: {e}")
                    continue
        
        logger.info(f"找到 {len(files)} 个Excel文件")
        
        return FileListResponse(
            files=files,
            total=len(files)
        )
        
    except Exception as e:
        logger.error(f"获取文件列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取文件列表失败")

@router.get("/read/{filename}", response_model=ExcelData, summary="读取Excel数据")
async def read_excel_data(
    filename: str,
    sheet_name: str = "Sheet1",
    output_path: str = Depends(get_output_path),
    logger = Depends(get_logger)
):
    """
    读取Excel文件数据
    
    - **filename**: 文件名
    - **sheet_name**: 工作表名称（默认Sheet1）
    """
    try:
        file_path = Path(output_path) / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="文件不存在")
        
        logger.info(f"读取Excel文件: {file_path}")
        
        # 读取Excel数据
        excel_data = await excel_service.read_excel_data(file_path, sheet_name)
        
        return excel_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"读取Excel数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"读取数据失败: {str(e)}")

@router.get("/templates", response_model=List[ExcelTemplate], summary="获取Excel模板")
async def get_excel_templates(
    logger = Depends(get_logger)
):
    """
    获取可用的Excel模板列表
    """
    try:
        # 返回预定义的模板
        templates = [
            ExcelTemplate(
                template_name="员工配偶信息报备模板",
                description="用于录入员工配偶的证券交易信息",
                headers=[
                    "交易日期", "证券代码", "证券名称", "交易类型", 
                    "交易数量", "交易价格", "交易金额", "相关人员", "关系"
                ],
                default_data=[],
                validation_rules={
                    "交易日期": {"required": True, "type": "date"},
                    "证券代码": {"required": True, "pattern": "^[0-9]{6}$"},
                    "证券名称": {"required": True, "maxLength": 50},
                    "交易类型": {"required": True, "enum": ["买入", "卖出"]},
                    "交易数量": {"required": True, "type": "number", "min": 1},
                    "交易价格": {"required": True, "type": "number", "min": 0},
                    "相关人员": {"required": True, "maxLength": 50},
                    "关系": {"required": True, "enum": ["配偶", "子女", "父母"]}
                }
            )
        ]
        
        logger.info(f"返回 {len(templates)} 个模板")
        
        return templates
        
    except Exception as e:
        logger.error(f"获取模板失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取模板失败")

@router.post("/validate", summary="验证Excel数据")
async def validate_excel_data(
    request: SaveExcelRequest,
    template_name: str = "员工配偶信息报备模板",
    logger = Depends(get_logger)
):
    """
    验证Excel数据是否符合模板要求
    
    - **request**: Excel数据
    - **template_name**: 模板名称
    """
    try:
        # 验证数据格式
        validation_result = await excel_service.validate_excel_data(
            data=request.data,
            template_name=template_name
        )
        
        return validation_result
        
    except Exception as e:
        logger.error(f"验证Excel数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"验证失败: {str(e)}")