from typing import List, Dict, Optional
from pydantic import BaseModel

class Message(BaseModel):
    role: str  # "system", "user", "assistant"
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    enable_thinking: Optional[bool] = None
    stream: Optional[bool] = False