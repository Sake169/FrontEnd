from openai import OpenAI
from config.settings import Settings
from core.exceptions import APIError

class QwenClient:
    def __init__(self, api_key: str = None, base_url: str = None):
        self.settings = Settings()
        self.client = OpenAI(
            api_key=api_key or self.settings.API_KEY,
            base_url=base_url or self.settings.BASE_URL
        )
    
    def chat_completion(self, messages: list, model: str = None, **kwargs) -> dict:
        """调用大模型API"""
        try:
            params = {
                "model": model or self.settings.DEFAULT_MODEL,
                "messages": messages,
                "response_format": {"type": "json_object"}  # 强制返回JSON
            }
            params.update(kwargs)  # 合并其他参数
            
            response = self.client.chat.completions.create(**params)
            return response.model_dump()  # 转换为字典
        except Exception as e:
            raise APIError(f"API调用失败: {str(e)}")