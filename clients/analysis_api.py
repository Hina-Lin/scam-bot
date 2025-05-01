"""
分析 API 客戶端

此模組提供與外部詐騙分析 API 互動的客戶端。
它處理發送訊息資料進行分析並處理回應。
"""

import requests
import json
import traceback
from utils.logger import get_client_logger

# 取得模組特定的日誌記錄器
logger = get_client_logger("analysis_api")

class AnalysisApiClient:
    """
    與外部詐騙分析 API 互動的客戶端。
    """
    
    def __init__(self, api_url=None):
        """
        初始化分析 API 客戶端。
        
        Args:
            api_url: 外部分析 API 的 URL（可選）
        """
        self.api_url = api_url
        self.headers = {"Content-Type": "application/json"}
    
    def analyze_text(self, data):
        """
        發送資料到外部 API 進行詐騙分析。
        
        Args:
            data: 包含訊息和上下文資料的字典
            
        Returns:
            dict: 包含標籤、可信度和回覆的分析結果
            
        Raises:
            Exception: 如果 API 未配置或返回錯誤
        """
        if not self.api_url:
            logger.error("API URL 未配置")
            raise Exception("API URL 未配置")
        
        try:
            logger.info(f"發送資料到分析 API: {self.api_url}")
            response = requests.post(
                self.api_url,
                headers=self.headers,
                data=json.dumps(data),
                timeout=5
            )
            
            if response.status_code == 200:
                logger.info("成功從 API 獲取分析結果")
                return response.json()
            else:
                logger.error(f"API 回應錯誤：{response.status_code}")
                raise Exception(f"API 返回狀態碼 {response.status_code}")
                
        except Exception as e:
            logger.error(f"發送資料到 API 時發生錯誤：{e}")
            logger.error(traceback.format_exc())
            raise
    
    def is_configured(self):
        """
        檢查 API 客戶端是否正確配置。
        
        Returns:
            bool: 如果設置了 API URL 則為 True，否則為 False
        """
        is_configured = self.api_url is not None and self.api_url.strip() != ""
        logger.info(f"API 客戶端配置狀態: {'已配置' if is_configured else '未配置'}")
        return is_configured
