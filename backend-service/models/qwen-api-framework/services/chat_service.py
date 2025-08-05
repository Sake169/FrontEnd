from typing import List, Optional
from core.models import ChatCompletionRequest, Message
from config.settings import Settings
from core.client import QwenClient
from services.prompt_templates import PromptTemplates

class ChatService:
    def __init__(self):
        self.client = QwenClient()
        self.settings = Settings()
        self.conversation_history = []  # 存储对话历史
    
    def simple_chat(self, user_message: str, model: str = None, enable_thinking: bool = False) -> str:
        # 添加用户消息到历史
        self.conversation_history.append(
            PromptTemplates.get_user_prompt(user_message)
        )
        
        # 构建消息列表：系统提示 + 历史对话
        messages = [PromptTemplates.get_system_prompt()] + self.conversation_history
        
        request = ChatCompletionRequest(
            model=model or self.settings.DEFAULT_MODEL,
            messages=messages,
            enable_thinking=enable_thinking
        )
        
        response = self.client.chat_completion(request)
        ai_response = response['choices'][0]['message']['content']
        
        # 添加AI回复到历史
        self.conversation_history.append(
            Message(role="assistant", content=ai_response)
        )
        
        return ai_response
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []
    
    def get_history(self) -> List[Message]:
        """获取完整对话历史"""
        return self.conversation_history