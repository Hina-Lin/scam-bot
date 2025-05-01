"""
配置模組

此模組從環境變數加載配置並提供配置值給應用程式。
"""

import os
from dotenv import load_dotenv

# 從 .env 檔案加載環境變數
load_dotenv()

class Config:
    """應用程式的配置容器。"""
    
    # LINE Bot 配置
    LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
    LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    
    # 外部 API 配置
    ANALYSIS_API_URL = os.getenv("ANALYSIS_API_URL")
    
    # LLM API 金鑰配置
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    
    # LLM 提供商選擇 (openai, gemini, openrouter)
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")
    LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-pro-exp-03-25")
    
    # 伺服器配置
    PORT = int(os.getenv("PORT", 10000))
    DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "t", "1")
    
    @classmethod
    def validate(cls):
        """
        驗證所有必要的配置值都已設置。
        
        Raises:
            ValueError: 如果任何必要的配置缺失
        """
        if not cls.LINE_CHANNEL_SECRET:
            raise ValueError("LINE_CHANNEL_SECRET 是必要的")
            
        if not cls.LINE_CHANNEL_ACCESS_TOKEN:
            raise ValueError("LINE_CHANNEL_ACCESS_TOKEN 是必要的")
        
        # ANALYSIS_API_URL 是可選的
        
        # 檢查是否設置了選擇的 LLM 提供商的 API 金鑰
        if cls.LLM_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            raise ValueError("使用 OpenAI 時，OPENAI_API_KEY 是必要的")
        elif cls.LLM_PROVIDER == "gemini" and not cls.GOOGLE_API_KEY:
            raise ValueError("使用 Gemini 時，GOOGLE_API_KEY 是必要的")
        elif cls.LLM_PROVIDER == "openrouter" and not cls.OPENROUTER_API_KEY:
            raise ValueError("使用 OpenRouter 時，OPENROUTER_API_KEY 是必要的")
        
        return True
