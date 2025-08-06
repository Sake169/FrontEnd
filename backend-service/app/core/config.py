from pydantic_settings import BaseSettings
from typing import List
import os
from pathlib import Path

class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基本信息
    app_name: str = "证券公司员工配偶信息报备系统API"
    app_version: str = "1.0.0"
    app_description: str = "处理文件上传、AI识别和Excel生成的后端服务"
    
    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8001
    debug: bool = True
    reload: bool = True
    
    # CORS配置
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Vite默认端口
        "http://127.0.0.1:5173",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
        "http://localhost:3004",
        "http://localhost:3005",
        "http://localhost:3006",
        "http://localhost:3007",
        "http://localhost:3008",
        "http://localhost:3009",  # 当前前端端口
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "http://127.0.0.1:3003",
        "http://127.0.0.1:3004",
        "http://127.0.0.1:3005",
        "http://127.0.0.1:3006",
        "http://127.0.0.1:3007",
        "http://127.0.0.1:3008",
        "http://127.0.0.1:3009"
    ]
    
    # 文件配置
    upload_dir: str = "uploads"
    output_dir: str = "outputs"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: List[str] = [
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
        "application/pdf"
    ]
    
    # AI模型配置
    ai_model_endpoint: str = ""
    ai_model_api_key: str = ""
    ai_model_timeout: int = 30
    
    # 数据库配置（预留）
    database_url: str = ""
    
    # 日志配置
    log_level: str = "INFO"
    log_file: str = "app.log"
    
    # 安全配置
    secret_key: str = "your-secret-key-here"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 确保目录存在
        Path(self.upload_dir).mkdir(exist_ok=True)
        Path(self.output_dir).mkdir(exist_ok=True)

# 创建全局配置实例
settings = Settings()