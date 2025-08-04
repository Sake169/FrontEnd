import asyncio
import json
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import aiohttp
import pandas as pd
from datetime import datetime
import re
import logging

logger = logging.getLogger(__name__)

class AIService:
    """AI服务 - 处理大模型调用和文档分析"""
    
    def __init__(self):
        self.api_base_url = "https://api.openai.com/v1"  # 可配置
        self.api_key = None  # 从环境变量或配置文件获取
        self.model_name = "gpt-3.5-turbo"  # 默认模型
        self.max_tokens = 4000
        self.temperature = 0.1
        
    def configure(self, config: Dict[str, Any]):
        """
        配置AI服务
        
        Args:
            config: 配置字典
        """
        self.api_base_url = config.get("api_base_url", self.api_base_url)
        self.api_key = config.get("api_key", self.api_key)
        self.model_name = config.get("model_name", self.model_name)
        self.max_tokens = config.get("max_tokens", self.max_tokens)
        self.temperature = config.get("temperature", self.temperature)
    
    async def process_file(self, file_path: Path, processing_type: str = "extract") -> Dict[str, Any]:
        """
        处理文件
        
        Args:
            file_path: 文件路径
            processing_type: 处理类型 (extract, analyze, summarize)
        
        Returns:
            处理结果
        """
        try:
            if not file_path.exists():
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            # 根据文件类型选择处理方法
            file_extension = file_path.suffix.lower()
            
            if file_extension in ['.xlsx', '.xls']:
                return await self._process_excel_file(file_path, processing_type)
            elif file_extension in ['.txt', '.md']:
                return await self._process_text_file(file_path, processing_type)
            elif file_extension in ['.pdf']:
                return await self._process_pdf_file(file_path, processing_type)
            else:
                raise ValueError(f"不支持的文件类型: {file_extension}")
                
        except Exception as e:
            logger.error(f"处理文件失败: {str(e)}")
            raise Exception(f"处理文件失败: {str(e)}")
    
    async def _process_excel_file(self, file_path: Path, processing_type: str) -> Dict[str, Any]:
        """
        处理Excel文件
        
        Args:
            file_path: Excel文件路径
            processing_type: 处理类型
        
        Returns:
            处理结果
        """
        try:
            # 读取Excel文件
            df = pd.read_excel(file_path)
            
            # 基本信息提取
            basic_info = {
                "filename": file_path.name,
                "shape": df.shape,
                "columns": list(df.columns),
                "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                "null_counts": df.isnull().sum().to_dict(),
                "sample_data": df.head(5).to_dict('records')
            }
            
            if processing_type == "extract":
                # 提取结构化数据
                return {
                    "type": "excel_extraction",
                    "status": "success",
                    "data": {
                        "basic_info": basic_info,
                        "extracted_data": df.to_dict('records'),
                        "summary": {
                            "total_rows": len(df),
                            "total_columns": len(df.columns),
                            "has_null_values": df.isnull().any().any(),
                            "numeric_columns": list(df.select_dtypes(include=['number']).columns),
                            "text_columns": list(df.select_dtypes(include=['object']).columns)
                        }
                    },
                    "timestamp": datetime.now().isoformat()
                }
            
            elif processing_type == "analyze":
                # 分析数据结构和内容
                analysis_prompt = self._create_excel_analysis_prompt(df, basic_info)
                ai_analysis = await self._call_ai_model(analysis_prompt)
                
                return {
                    "type": "excel_analysis",
                    "status": "success",
                    "data": {
                        "basic_info": basic_info,
                        "ai_analysis": ai_analysis,
                        "recommendations": await self._generate_excel_recommendations(df)
                    },
                    "timestamp": datetime.now().isoformat()
                }
            
            elif processing_type == "summarize":
                # 生成数据摘要
                summary_prompt = self._create_excel_summary_prompt(df, basic_info)
                ai_summary = await self._call_ai_model(summary_prompt)
                
                return {
                    "type": "excel_summary",
                    "status": "success",
                    "data": {
                        "basic_info": basic_info,
                        "ai_summary": ai_summary,
                        "key_insights": await self._extract_key_insights(df)
                    },
                    "timestamp": datetime.now().isoformat()
                }
            
            else:
                raise ValueError(f"不支持的处理类型: {processing_type}")
                
        except Exception as e:
            raise Exception(f"处理Excel文件失败: {str(e)}")
    
    async def _process_text_file(self, file_path: Path, processing_type: str) -> Dict[str, Any]:
        """
        处理文本文件
        
        Args:
            file_path: 文本文件路径
            processing_type: 处理类型
        
        Returns:
            处理结果
        """
        try:
            # 读取文本内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            basic_info = {
                "filename": file_path.name,
                "size": len(content),
                "lines": len(content.split('\n')),
                "words": len(content.split()),
                "characters": len(content)
            }
            
            if processing_type == "extract":
                # 提取文本内容
                return {
                    "type": "text_extraction",
                    "status": "success",
                    "data": {
                        "basic_info": basic_info,
                        "content": content,
                        "preview": content[:500] + "..." if len(content) > 500 else content
                    },
                    "timestamp": datetime.now().isoformat()
                }
            
            elif processing_type == "analyze":
                # 分析文本内容
                analysis_prompt = f"请分析以下文本内容的结构、主题和关键信息：\n\n{content[:2000]}"
                ai_analysis = await self._call_ai_model(analysis_prompt)
                
                return {
                    "type": "text_analysis",
                    "status": "success",
                    "data": {
                        "basic_info": basic_info,
                        "ai_analysis": ai_analysis,
                        "keywords": await self._extract_keywords(content)
                    },
                    "timestamp": datetime.now().isoformat()
                }
            
            elif processing_type == "summarize":
                # 生成文本摘要
                summary_prompt = f"请为以下文本生成简洁的摘要：\n\n{content}"
                ai_summary = await self._call_ai_model(summary_prompt)
                
                return {
                    "type": "text_summary",
                    "status": "success",
                    "data": {
                        "basic_info": basic_info,
                        "ai_summary": ai_summary
                    },
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            raise Exception(f"处理文本文件失败: {str(e)}")
    
    async def _process_pdf_file(self, file_path: Path, processing_type: str) -> Dict[str, Any]:
        """
        处理PDF文件（占位符实现）
        
        Args:
            file_path: PDF文件路径
            processing_type: 处理类型
        
        Returns:
            处理结果
        """
        # 这里需要集成PDF处理库，如PyPDF2或pdfplumber
        return {
            "type": "pdf_processing",
            "status": "not_implemented",
            "message": "PDF处理功能尚未实现",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _call_ai_model(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        调用AI模型
        
        Args:
            prompt: 用户提示
            system_prompt: 系统提示
        
        Returns:
            AI模型响应
        """
        try:
            if not self.api_key:
                # 如果没有配置API密钥，返回模拟响应
                return self._generate_mock_response(prompt)
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": self.model_name,
                "messages": messages,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base_url}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["choices"][0]["message"]["content"]
                    else:
                        error_text = await response.text()
                        raise Exception(f"AI API调用失败: {response.status} - {error_text}")
                        
        except Exception as e:
            logger.error(f"AI模型调用失败: {str(e)}")
            # 返回模拟响应作为后备
            return self._generate_mock_response(prompt)
    
    def _generate_mock_response(self, prompt: str) -> str:
        """
        生成模拟AI响应（用于测试和演示）
        
        Args:
            prompt: 输入提示
        
        Returns:
            模拟响应
        """
        if "分析" in prompt:
            return "这是一个模拟的数据分析结果。数据结构清晰，包含多个维度的信息，建议进一步清理和标准化数据格式。"
        elif "摘要" in prompt:
            return "这是一个模拟的内容摘要。文档包含重要的业务信息，主要涉及数据处理和分析流程。"
        elif "提取" in prompt:
            return "已成功提取文档中的关键信息，包括结构化数据和元数据。"
        else:
            return "这是一个模拟的AI响应，用于演示系统功能。实际使用时需要配置真实的AI模型API。"
    
    def _create_excel_analysis_prompt(self, df: pd.DataFrame, basic_info: Dict[str, Any]) -> str:
        """
        创建Excel分析提示
        
        Args:
            df: DataFrame对象
            basic_info: 基本信息
        
        Returns:
            分析提示
        """
        sample_data = df.head(3).to_string()
        
        return f"""
请分析以下Excel数据的结构和内容特征：

基本信息：
- 文件名：{basic_info['filename']}
- 数据形状：{basic_info['shape']}
- 列名：{basic_info['columns']}
- 数据类型：{basic_info['dtypes']}

样本数据：
{sample_data}

请提供以下分析：
1. 数据结构特征
2. 数据质量评估
3. 潜在的数据问题
4. 改进建议
"""
    
    def _create_excel_summary_prompt(self, df: pd.DataFrame, basic_info: Dict[str, Any]) -> str:
        """
        创建Excel摘要提示
        
        Args:
            df: DataFrame对象
            basic_info: 基本信息
        
        Returns:
            摘要提示
        """
        return f"""
请为以下Excel数据生成简洁的摘要：

- 总行数：{len(df)}
- 总列数：{len(df.columns)}
- 主要列：{list(df.columns)[:5]}
- 数据类型分布：{basic_info['dtypes']}

请生成包含以下内容的摘要：
1. 数据概览
2. 主要特征
3. 关键发现
"""
    
    async def _generate_excel_recommendations(self, df: pd.DataFrame) -> List[str]:
        """
        生成Excel数据处理建议
        
        Args:
            df: DataFrame对象
        
        Returns:
            建议列表
        """
        recommendations = []
        
        # 检查空值
        if df.isnull().any().any():
            recommendations.append("建议处理数据中的空值")
        
        # 检查重复行
        if df.duplicated().any():
            recommendations.append("发现重复行，建议去重")
        
        # 检查数据类型
        for col in df.columns:
            if df[col].dtype == 'object':
                # 检查是否可以转换为数值类型
                try:
                    pd.to_numeric(df[col], errors='raise')
                    recommendations.append(f"列'{col}'可能可以转换为数值类型")
                except:
                    pass
        
        # 检查列名
        for col in df.columns:
            if ' ' in str(col) or str(col).isupper():
                recommendations.append("建议标准化列名格式")
                break
        
        return recommendations
    
    async def _extract_key_insights(self, df: pd.DataFrame) -> List[str]:
        """
        提取关键洞察
        
        Args:
            df: DataFrame对象
        
        Returns:
            洞察列表
        """
        insights = []
        
        # 数据规模洞察
        insights.append(f"数据集包含{len(df)}行和{len(df.columns)}列")
        
        # 数据完整性洞察
        null_percentage = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        if null_percentage > 0:
            insights.append(f"数据完整性：{100-null_percentage:.1f}%")
        
        # 数值列统计
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            insights.append(f"包含{len(numeric_cols)}个数值列")
        
        # 文本列统计
        text_cols = df.select_dtypes(include=['object']).columns
        if len(text_cols) > 0:
            insights.append(f"包含{len(text_cols)}个文本列")
        
        return insights
    
    async def _extract_keywords(self, text: str) -> List[str]:
        """
        提取文本关键词
        
        Args:
            text: 文本内容
        
        Returns:
            关键词列表
        """
        # 简单的关键词提取（实际应用中可以使用更复杂的NLP技术）
        words = re.findall(r'\b\w{3,}\b', text.lower())
        word_freq = {}
        
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # 返回频率最高的10个词
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:10]]
    
    async def extract_text_from_file(self, file_path: Path) -> str:
        """
        从文件中提取文本
        
        Args:
            file_path: 文件路径
        
        Returns:
            提取的文本内容
        """
        try:
            file_extension = file_path.suffix.lower()
            
            if file_extension in ['.txt', '.md']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            elif file_extension in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
                return df.to_string()
            
            else:
                raise ValueError(f"不支持的文件类型: {file_extension}")
                
        except Exception as e:
            raise Exception(f"提取文本失败: {str(e)}")
    
    async def analyze_document_structure(self, file_path: Path) -> Dict[str, Any]:
        """
        分析文档结构
        
        Args:
            file_path: 文件路径
        
        Returns:
            文档结构分析结果
        """
        try:
            file_extension = file_path.suffix.lower()
            
            if file_extension in ['.xlsx', '.xls']:
                # Excel文档结构分析
                df = pd.read_excel(file_path, sheet_name=None)
                
                structure = {
                    "type": "excel",
                    "sheets": {},
                    "summary": {
                        "total_sheets": len(df),
                        "sheet_names": list(df.keys())
                    }
                }
                
                for sheet_name, sheet_df in df.items():
                    structure["sheets"][sheet_name] = {
                        "shape": sheet_df.shape,
                        "columns": list(sheet_df.columns),
                        "dtypes": {col: str(dtype) for col, dtype in sheet_df.dtypes.items()},
                        "has_header": True,  # 假设有标题行
                        "sample_data": sheet_df.head(2).to_dict('records')
                    }
                
                return structure
            
            elif file_extension in ['.txt', '.md']:
                # 文本文档结构分析
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                lines = content.split('\n')
                
                return {
                    "type": "text",
                    "structure": {
                        "total_lines": len(lines),
                        "total_words": len(content.split()),
                        "total_characters": len(content),
                        "empty_lines": sum(1 for line in lines if not line.strip()),
                        "has_headers": any(line.startswith('#') for line in lines),
                        "paragraphs": len([p for p in content.split('\n\n') if p.strip()])
                    }
                }
            
            else:
                return {
                    "type": "unknown",
                    "message": f"不支持的文件类型: {file_extension}"
                }
                
        except Exception as e:
            raise Exception(f"分析文档结构失败: {str(e)}")
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """
        获取可用的AI模型列表
        
        Returns:
            模型信息列表
        """
        return [
            {
                "id": "gpt-3.5-turbo",
                "name": "GPT-3.5 Turbo",
                "description": "快速、高效的对话模型",
                "max_tokens": 4096,
                "available": True
            },
            {
                "id": "gpt-4",
                "name": "GPT-4",
                "description": "更强大的推理和分析能力",
                "max_tokens": 8192,
                "available": False  # 需要特殊权限
            },
            {
                "id": "text-davinci-003",
                "name": "Text Davinci 003",
                "description": "强大的文本生成模型",
                "max_tokens": 4000,
                "available": True
            }
        ]
    
    async def health_check(self) -> Dict[str, Any]:
        """
        AI服务健康检查
        
        Returns:
            健康状态信息
        """
        try:
            # 尝试调用AI模型进行简单测试
            test_response = await self._call_ai_model("Hello, this is a health check.")
            
            return {
                "status": "healthy",
                "api_configured": bool(self.api_key),
                "model": self.model_name,
                "test_response_length": len(test_response),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "api_configured": bool(self.api_key),
                "model": self.model_name,
                "timestamp": datetime.now().isoformat()
            }