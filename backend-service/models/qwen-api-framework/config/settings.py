class Settings:
    BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    API_KEY = "sk-7517c06221974628bd8b2ea6f01bf2bc"
    
    # 模型配置
    MODELS = {
        "instruct": "qwen3-235b-a22b-instruct-2507",
        "thinking": "qwen3-235b-a22b-thinking-2507"
    }
    
    # 默认配置
    DEFAULT_MODEL = MODELS["instruct"]
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_MAX_TOKENS = 2048