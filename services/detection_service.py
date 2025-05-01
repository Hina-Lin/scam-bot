"""
檢測服務 - 領域服務層

此服務負責分析訊息並檢測潛在的詐騙。
它可以使用本地關鍵詞檢測或整合外部 API。
"""

from utils.logger import get_service_logger

# 取得模組特定的日誌記錄器
logger = get_service_logger("detection")

class DetectionService:
    """
    用於檢測訊息中詐騙的服務。
    可以根據配置使用本地檢測或外部 API。
    """
    
    def __init__(self, analysis_client=None):
        """
        初始化檢測服務。
        
        Args:
            analysis_client: 可選的外部詐騙分析 API 客戶端
        """
        self.analysis_client = analysis_client
        self.scam_keywords = [
            "怎麼投資", "怎麼給你", "錢怎麼轉", 
            "要匯到哪", "我相信你", "我沒有別人可以相信了"
        ]
    
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
        """
        # 如果配置並可用，則使用外部 API 客戶端
        if self.analysis_client:
            try:
                logger.info("嘗試使用外部 API 分析訊息")
                # 準備 API 的數據
                analysis_data = {
                    "user_id": user_id,
                    "message": message_text,
                    "chat_history": chat_history,
                    "user_profile": user_profile
                }
                
                # 呼叫外部 API
                return self.analysis_client.analyze_text(analysis_data)
            except Exception as e:
                # 記錄錯誤並回退到本地檢測
                logger.error(f"外部 API 錯誤: {e}")
                logger.info("回退到本地關鍵詞檢測")
        
        # 使用關鍵詞進行本地檢測
        return self._local_detection(message_text)
    
    def _local_detection(self, text):
        """
        執行基於關鍵詞的本地詐騙檢測。
        
        Args:
            text: 要分析的文字
            
        Returns:
            dict: 分析結果
        """
        logger.info("使用本地關鍵詞檢測")
        if any(word in text for word in self.scam_keywords):
            logger.warning(f"偵測到關鍵詞，標記為詐騙")
            return {
                "label": "scam",
                "confidence": 0.9,
                "reply": "這是我投資成功的故事，你想聽嗎？"
            }
        else:
            logger.info("未偵測到詐騙關鍵詞")
            return {
                "label": "safe",
                "confidence": 0.1,
                "reply": "哈哈你說得真有趣，我懂你！"
            }
