#!/usr/bin/env python3
"""
后端服务启动脚本
"""

import uvicorn
import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """
    启动FastAPI服务
    """
    print("正在启动证券公司员工配偶信息报备系统后端服务...")
    print("API文档地址: http://localhost:8000/docs")
    print("服务地址: http://localhost:8000")
    print("按 Ctrl+C 停止服务")
    print("-" * 50)
    
    # 创建必要的目录
    upload_dir = Path("uploads")
    output_dir = Path("outputs")
    upload_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)
    
    # 启动服务
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["."],
        log_level="info"
    )

if __name__ == "__main__":
    main()