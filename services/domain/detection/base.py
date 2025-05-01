from abc import ABC, abstractmethod

class DetectionStrategy(ABC):
    """檢測策略的抽象基類"""
    
    @abstractmethod
    def analyze(self, message_text, user_id=None, chat_history=None, user_profile=None):
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
        pass