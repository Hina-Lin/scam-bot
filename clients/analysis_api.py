"""
分析 API 客戶端

此模組提供與外部詐騙分析 API 互動的客戶端。
它處理發送訊息資料進行分析並處理回應。
"""

import requests
import json
from utils.logger import get_client_logger
from utils.error_handler import ApiError, with_error_handling

# 取得模組特定的日誌記錄器
logger = get_client_logger("analysis_api")

class AnalysisApiClient:
    """與外部詐騙分析 API 互動的客戶端"""
    
    def __init__(self, api_url=None):
        """
        初始化分析 API 客戶端。
        
        Args:
            api_url: 外部分析 API 的 URL（可選）
        """
        self.api_url = api_url
        self.headers = {"Content-Type": "application/json"}
    
    @with_error_handling(reraise=True)
    def analyze_text(self, data):
        """
        發送資料到外部 API 進行詐騙分析。
        
        Args:
            data: 包含訊息和上下文資料的字典
            
        Returns:
            dict: 包含標籤、可信度和回覆的分析結果
            
        Raises:
            ApiError: 如果 API 未配置或返回錯誤
        """
        if not self.api_url:
            logger.error("API URL 未配置")
            raise ApiError("API URL 未配置", status_code=400)
        
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
                error_msg = f"API 回應錯誤：{response.status_code}"
                logger.error(error_msg)
                if response.text:
                    logger.error(f"API 回應內容：{response.text}")
                raise ApiError(error_msg, status_code=response.status_code)
                
        except requests.RequestException as e:
            error_msg = f"API 請求異常：{str(e)}"
            logger.error(error_msg)
            raise ApiError(error_msg, original_error=e)
        except json.JSONDecodeError as e:
            error_msg = f"API 回應解析失敗：{str(e)}"
            logger.error(error_msg)
            raise ApiError(error_msg, original_error=e)
        except Exception as e:
            error_msg = f"發送資料到 API 時發生未知錯誤：{str(e)}"
            logger.error(error_msg)
            raise ApiError(error_msg, original_error=e)
    
    def is_configured(self):
        """
        檢查 API 客戶端是否正確配置。
        
        Returns:
            bool: 如果設置了 API URL 則為 True，否則為 False
        """
        is_configured = self.api_url is not None and self.api_url.strip() != ""
        logger.info(f"API 客戶端配置狀態: {'已配置' if is_configured else '未配置'}")
        return is_configured
