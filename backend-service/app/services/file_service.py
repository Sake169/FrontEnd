import aiofiles
import os
import uuid
from pathlib import Path
from typing import Optional, Dict, Any
import hashlib
from datetime import datetime
import mimetypes

class FileService:
    """文件处理服务"""
    
    def __init__(self):
        self.upload_dir = Path("uploads")
        self.upload_dir.mkdir(exist_ok=True)
    
    async def save_uploaded_file(
        self, 
        file_content: bytes, 
        filename: str, 
        upload_dir: Optional[str] = None
    ) -> Path:
        """
        保存上传的文件
        
        Args:
            file_content: 文件内容
            filename: 原始文件名
            upload_dir: 上传目录（可选）
        
        Returns:
            保存的文件路径
        """
        try:
            # 确定保存目录
            save_dir = Path(upload_dir) if upload_dir else self.upload_dir
            save_dir.mkdir(exist_ok=True)
            
            # 生成唯一文件名
            file_extension = Path(filename).suffix
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = save_dir / unique_filename
            
            # 异步保存文件
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_content)
            
            return file_path
            
        except Exception as e:
            raise Exception(f"保存文件失败: {str(e)}")
    
    async def get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """
        获取文件信息
        
        Args:
            file_path: 文件路径
        
        Returns:
            文件信息字典
        """
        try:
            if not file_path.exists():
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            stat = file_path.stat()
            
            # 计算文件哈希
            file_hash = await self._calculate_file_hash(file_path)
            
            # 获取MIME类型
            mime_type, _ = mimetypes.guess_type(str(file_path))
            
            return {
                "name": file_path.name,
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime),
                "modified": datetime.fromtimestamp(stat.st_mtime),
                "mime_type": mime_type,
                "hash": file_hash,
                "extension": file_path.suffix.lower()
            }
            
        except Exception as e:
            raise Exception(f"获取文件信息失败: {str(e)}")
    
    async def _calculate_file_hash(self, file_path: Path) -> str:
        """
        计算文件MD5哈希值
        
        Args:
            file_path: 文件路径
        
        Returns:
            MD5哈希值
        """
        hash_md5 = hashlib.md5()
        
        async with aiofiles.open(file_path, 'rb') as f:
            while chunk := await f.read(8192):
                hash_md5.update(chunk)
        
        return hash_md5.hexdigest()
    
    async def delete_file(self, file_path: Path) -> bool:
        """
        删除文件
        
        Args:
            file_path: 文件路径
        
        Returns:
            是否删除成功
        """
        try:
            if file_path.exists():
                file_path.unlink()
                return True
            return False
            
        except Exception as e:
            raise Exception(f"删除文件失败: {str(e)}")
    
    async def move_file(self, source_path: Path, target_path: Path) -> bool:
        """
        移动文件
        
        Args:
            source_path: 源文件路径
            target_path: 目标文件路径
        
        Returns:
            是否移动成功
        """
        try:
            if not source_path.exists():
                raise FileNotFoundError(f"源文件不存在: {source_path}")
            
            # 确保目标目录存在
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 移动文件
            source_path.rename(target_path)
            
            return True
            
        except Exception as e:
            raise Exception(f"移动文件失败: {str(e)}")
    
    async def copy_file(self, source_path: Path, target_path: Path) -> bool:
        """
        复制文件
        
        Args:
            source_path: 源文件路径
            target_path: 目标文件路径
        
        Returns:
            是否复制成功
        """
        try:
            if not source_path.exists():
                raise FileNotFoundError(f"源文件不存在: {source_path}")
            
            # 确保目标目录存在
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 异步复制文件
            async with aiofiles.open(source_path, 'rb') as src:
                async with aiofiles.open(target_path, 'wb') as dst:
                    while chunk := await src.read(8192):
                        await dst.write(chunk)
            
            return True
            
        except Exception as e:
            raise Exception(f"复制文件失败: {str(e)}")
    
    async def list_files(
        self, 
        directory: Path, 
        pattern: str = "*",
        recursive: bool = False
    ) -> list[Dict[str, Any]]:
        """
        列出目录中的文件
        
        Args:
            directory: 目录路径
            pattern: 文件匹配模式
            recursive: 是否递归搜索
        
        Returns:
            文件信息列表
        """
        try:
            if not directory.exists():
                return []
            
            files = []
            
            if recursive:
                file_paths = directory.rglob(pattern)
            else:
                file_paths = directory.glob(pattern)
            
            for file_path in file_paths:
                if file_path.is_file():
                    file_info = await self.get_file_info(file_path)
                    file_info["path"] = str(file_path)
                    files.append(file_info)
            
            return files
            
        except Exception as e:
            raise Exception(f"列出文件失败: {str(e)}")
    
    def validate_file_type(self, filename: str, allowed_types: list[str]) -> bool:
        """
        验证文件类型
        
        Args:
            filename: 文件名
            allowed_types: 允许的文件类型列表
        
        Returns:
            是否为允许的文件类型
        """
        file_extension = Path(filename).suffix.lower()
        return file_extension in [ext.lower() for ext in allowed_types]
    
    def validate_file_size(self, file_size: int, max_size: int) -> bool:
        """
        验证文件大小
        
        Args:
            file_size: 文件大小（字节）
            max_size: 最大允许大小（字节）
        
        Returns:
            是否在允许的大小范围内
        """
        return file_size <= max_size
    
    async def cleanup_old_files(
        self, 
        directory: Path, 
        max_age_days: int = 7
    ) -> int:
        """
        清理旧文件
        
        Args:
            directory: 目录路径
            max_age_days: 最大保留天数
        
        Returns:
            删除的文件数量
        """
        try:
            if not directory.exists():
                return 0
            
            deleted_count = 0
            current_time = datetime.now().timestamp()
            max_age_seconds = max_age_days * 24 * 60 * 60
            
            for file_path in directory.iterdir():
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > max_age_seconds:
                        await self.delete_file(file_path)
                        deleted_count += 1
            
            return deleted_count
            
        except Exception as e:
            raise Exception(f"清理文件失败: {str(e)}")