from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import json
import shutil
from pathlib import Path
from typing import Optional
import pandas as pd
from pydantic import BaseModel
import aiofiles

# 创建FastAPI应用
app = FastAPI(
    title="证券公司员工配偶信息报备系统API",
    description="处理文件上传、AI识别和Excel生成的后端服务",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建必要的目录
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="."), name="static")

# 数据模型
class RelatedPersonInfo(BaseModel):
    name: str
    relationship: str
    idNumber: str
    phone: str
    description: Optional[str] = None

class UploadResponse(BaseModel):
    success: bool
    message: str
    excelUrl: Optional[str] = None
    fileName: Optional[str] = None

class SaveExcelRequest(BaseModel):
    fileName: str
    data: list
    sheets: Optional[list] = None

@app.get("/")
async def root():
    return {"message": "证券公司员工配偶信息报备系统API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API服务运行正常"}

@app.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    relatedPersonInfo: str = Form(...)
):
    """
    上传文件并处理
    """
    try:
        # 解析相关人员信息
        person_info = json.loads(relatedPersonInfo)
        
        # 验证文件类型
        if not (file.content_type.startswith('image/') or file.content_type == 'application/pdf'):
            raise HTTPException(status_code=400, detail="只支持图片和PDF文件")
        
        # 保存上传的文件
        file_path = UPLOAD_DIR / file.filename
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        print(f"文件已保存: {file_path}")
        print(f"相关人员信息: {person_info}")
        
        # TODO: 这里应该调用AI模型进行图片/PDF识别
        # 目前直接返回固定的Excel文件
        
        # 复制example.xlsx到输出目录
        example_file = Path("../example.xlsx")
        if example_file.exists():
            output_file = OUTPUT_DIR / "processed_result.xlsx"
            shutil.copy2(example_file, output_file)
            
            return UploadResponse(
                success=True,
                message=f"文件上传成功，已为{person_info['name']}生成Excel报表",
                excelUrl="/download/processed_result.xlsx",
                fileName="processed_result.xlsx"
            )
        else:
            # 如果example.xlsx不存在，创建一个示例Excel
            sample_data = {
                '交易日期': ['2024-01-15', '2024-01-16', '2024-01-17'],
                '证券代码': ['000001', '000002', '000003'],
                '证券名称': ['平安银行', '万科A', '国农科技'],
                '交易类型': ['买入', '卖出', '买入'],
                '交易数量': [1000, 500, 2000],
                '交易价格': [10.50, 25.30, 8.75],
                '交易金额': [10500.00, 12650.00, 17500.00],
                '相关人员': [person_info['name']] * 3,
                '关系': [person_info['relationship']] * 3
            }
            
            df = pd.DataFrame(sample_data)
            output_file = OUTPUT_DIR / "processed_result.xlsx"
            df.to_excel(output_file, index=False)
            
            return UploadResponse(
                success=True,
                message=f"文件上传成功，已为{person_info['name']}生成Excel报表",
                excelUrl="/download/processed_result.xlsx",
                fileName="processed_result.xlsx"
            )
            
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="相关人员信息格式错误")
    except Exception as e:
        print(f"处理文件时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理文件时出错: {str(e)}")

@app.get("/download/{filename}")
async def download_file(filename: str):
    """
    下载生成的Excel文件
    """
    file_path = OUTPUT_DIR / filename
    
    # 如果文件不存在，尝试从根目录获取example.xlsx
    if not file_path.exists():
        example_path = Path("../example.xlsx")
        if example_path.exists():
            return FileResponse(
                path=example_path,
                filename=filename,
                media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        else:
            raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@app.post("/save-excel")
async def save_excel_data(request: SaveExcelRequest):
    """
    保存编辑后的Excel数据
    """
    try:
        # 将数据转换为DataFrame
        df = pd.DataFrame(request.data[1:], columns=request.data[0] if request.data else [])
        
        # 保存到文件
        output_file = OUTPUT_DIR / request.fileName
        df.to_excel(output_file, index=False)
        
        return {"success": True, "message": "Excel数据保存成功"}
        
    except Exception as e:
        print(f"保存Excel数据时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"保存数据时出错: {str(e)}")

@app.get("/files")
async def list_files():
    """
    列出所有可用的文件
    """
    files = []
    
    # 列出输出目录中的文件
    if OUTPUT_DIR.exists():
        for file_path in OUTPUT_DIR.glob("*.xlsx"):
            files.append({
                "name": file_path.name,
                "size": file_path.stat().st_size,
                "modified": file_path.stat().st_mtime
            })
    
    return {"files": files}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)