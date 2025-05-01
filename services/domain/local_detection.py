"""
本地檢測策略

此模組實現了基於本地規則的詐騙檢測策略。
將來會實現 cosine 相似度計算和調用 agent。
"""

from .detection_strategy import DetectionStrategy
from utils.logger import get_service_logger
from utils.error_handler import DetectionError, with_error_handling

# 取得模組特定的日誌記錄器
logger = get_service_logger("local_detection")

class LocalDetectionStrategy(DetectionStrategy):
    """
    基於本地規則的檢測策略。
    將來會實現基於 cosine 相似度和 agent 的檢測。
    """
    
    def __init__(self):
        """初始化本地檢測策略。"""
        # 未來會在此初始化模型或其他資源
        pass
    
    @with_error_handling(reraise=True)
    def analyze(self, message_text, user_id=None, chat_history=None, user_profile=None):
        """
        使用本地規則分析訊息。
        
        Args:
            message_text: 要分析的文字
            user_id: 可選的使用者 ID 作為上下文
            chat_history: 可選的聊天歷史作為上下文
            user_profile: 可選的使用者資料
            
        Returns:
            dict: 包含標籤、可信度和回覆的分析結果
            
        Raises:
            DetectionError: 如果檢測過程中發生錯誤
        """
        logger.info("使用本地檢測策略 - 當前為佔位實現")
        
        # 檢查輸入
        if not message_text or not isinstance(message_text, str):
            error_msg = "訊息文本必須是非空字串"
            logger.error(error_msg)
            raise DetectionError(error_msg, status_code=400)
        
        # TODO: 實現實際的檢測邏輯
        # 1. 使用 cosine 相似度計算
        # 2. 調用 agent 進行分析
        
        # 目前返回安全標籤的佔位實現
        try:
            return {
                "label": "safe",
                "confidence": 0.5,
                "reply": "您好，有什麼我可以幫忙的嗎？"
            }
        except Exception as e:
            error_msg = f"本地檢測過程中發生錯誤: {str(e)}"
            logger.error(error_msg)
            raise DetectionError(error_msg, original_error=e)
