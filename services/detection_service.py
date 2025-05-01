"""
檢測服務 - 領域服務層

此服務負責分析訊息並檢測潛在的詐騙。
作為入口點，根據配置選擇使用 API 或本地檢測策略。
"""

from utils.logger import get_service_logger
from .domain.local_detection import LocalDetectionStrategy
from .domain.api_detection import ApiDetectionStrategy

# 取得模組特定的日誌記錄器
logger = get_service_logger("detection")

# === 主要入口點 ===
class DetectionService:
    """詐騙檢測服務，根據配置選擇使用 API 或本地檢測策略"""
    
    def __init__(self, analysis_client=None):
        """
        初始化檢測服務，根據是否有 API 客戶端來選擇適當的策略。
        
        Args:
            analysis_client: 可選的外部詐騙分析 API 客戶端
        """
        # 根據是否提供 API 客戶端決定使用哪種策略
        if analysis_client:
            self.strategy = ApiDetectionStrategy(analysis_client)
            logger.info("使用 API 檢測策略")
        else:
            self.strategy = LocalDetectionStrategy()
            logger.info("使用本地檢測策略")
    
    def analyze_message(self, message_text, user_id=None, chat_history=None, user_profile=None):
        """
        分析訊息以檢測是否為潛在詐騙。
        
        Args:
            message_text: 要分析的文字
            user_id: 可選的使用者 ID 作為上下文
            chat_history: 可選的聊天歷史作為上下文
            user_profile: 可選的使用者資料
            
        Returns:
            dict: 包含標籤、可信度和回覆的分析結果
            
        Raises:
            Exception: 如果檢測過程中發生錯誤
        """
        try:
            return self.strategy.analyze(message_text, user_id, chat_history, user_profile)
        except Exception as e:
            logger.error(f"檢測過程中發生錯誤: {str(e)}")
            # 重新拋出異常，讓上層處理
            raise
