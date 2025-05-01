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
        
        return True
