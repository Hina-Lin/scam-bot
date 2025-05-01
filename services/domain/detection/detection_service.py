"""
檢測服務 - 領域服務層

此服務負責分析訊息並檢測潛在的詐騙。
作為入口點，根據配置選擇使用 API 或本地檢測策略。
"""

from typing import Dict, List, Any, Optional
from utils.logger import get_service_logger
from .local_detection import LocalDetectionStrategy
from .api_detection import ApiDetectionStrategy

# 取得模組特定的日誌記錄器
logger = get_service_logger("detection")

# === 主要接口和實現 ===

class DetectionService:
    """詐騙檢測服務，根據配置選擇使用 API 或本地檢測策略"""
    
    def __init__(self, analysis_client: Optional[Any] = None):
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
            # 使用增強的本地檢測策略（基於ADK agent和相似度分析）
            self.strategy = LocalDetectionStrategy()
            logger.info("使用增強的本地檢測策略（包含ADK agent和相似度分析）")
    
    def analyze_message(self, message_text: str, user_id: Optional[str] = None, 
                      chat_history: Optional[List[str]] = None, 
                      user_profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        分析訊息以檢測是否為潛在詐騙。
        
        Args:
            message_text: 要分析的文字
            user_id: 可選的使用者 ID 作為上下文
            chat_history: 可選的聊天歷史作為上下文
            user_profile: 可選的使用者資料
            
        Returns:
            Dict[str, Any]: 包含標籤、可信度和回覆的分析結果
            
        Raises:
            Exception: 如果檢測過程中發生錯誤
        """
        try:
            # 呼叫當前策略的 analyze 方法
            # 注意：兩個策略 (Local 和 API) 現在都不接受 chat_history
            logger.debug(f"呼叫策略 {type(self.strategy).__name__} 的 analyze 方法")
            return self.strategy.analyze(message_text, user_id=user_id, user_profile=user_profile)
        except Exception as e:
            # 記錄詳細錯誤，包括策略類型
            strategy_type = type(self.strategy).__name__
            logger.error(f"使用 {strategy_type} 進行檢測時發生錯誤: {str(e)}", exc_info=True)
            raise
