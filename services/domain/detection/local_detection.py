"""
本地檢測策略

此模組實現了基於本地規則的詐騙檢測策略。
使用 ADK agent 進行詐騙檢測。
"""

from typing import Dict, List, Any, Optional, Union
import json
import os
import re
from pathlib import Path

from .base import DetectionStrategy
from utils.logger import get_service_logger
from utils.error_handler import DetectionError, with_error_handling
from utils.conversation_formatter import format_conversation
from utils.agents.agent_factory import create_agent

# 設定預設資料檔案路徑
PROJECT_ROOT = os.path.abspath(os.path.join(__file__, '../../../..'))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
SCAM_DATA_PATH = os.path.join(DATA_DIR, 'scam_data.json')

# 取得模組特定的日誌記錄器
logger = get_service_logger("local_detection")

# 加載詐騙範本資料
def _load_scam_data() -> Dict[str, Any]:
    """
    載入詐騙範本資料，包含範例和關鍵字。
    
    Returns:
        Dict[str, Any]: 詐騙範例和關鍵字數據
    """
    try:
        with open(SCAM_DATA_PATH, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"無法載入詐騙範本資料: {str(e)}")
        # 返回預設的最小資料
        return {
            "scam_examples": [],
            "keywords": []
        }

class LocalDetectionStrategy(DetectionStrategy):
    """
    基於本地規則和 agent 的檢測策略。
    """
    
    def __init__(self):
        """初始化本地檢測策略。"""
        # 載入詐騙樣本和關鍵詞資料
        self.data = _load_scam_data()
        self.keywords = self.data.get("keywords", [])
        
        logger.info(f"載入了 {len(self.keywords)} 個關鍵詞")
        
        # 初始化詐騙檢測 agent
        self.agent = create_agent(agent_type="scam_detection")
        logger.info("本地檢測策略初始化完成，已載入詐騙檢測 agent")
    
    def _keyword_analysis(self, message_text: str) -> Dict[str, Any]:
        """
        基於關鍵詞分析訊息，檢查詐騙指標。
        
        Args:
            message_text: 要分析的文字
            
        Returns:
            Dict: 包含檢測到的關鍵詞和評分的分析結果
        """
        # 計算詐騙關鍵詞的出現次數
        keyword_count = 0
        found_keywords = []
        
        # 檢查每個關鍵詞
        for keyword in self.keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', message_text, re.IGNORECASE):
                keyword_count += 1
                found_keywords.append(keyword)
        
        # 計算關鍵詞密度（關鍵詞數量 / 總字數）
        total_words = len(message_text.split())
        keyword_density = keyword_count / max(total_words, 1)
        
        # 基於關鍵詞密度和數量的風險評估
        risk_score = min(1.0, (keyword_count * 0.1) + (keyword_density * 2))
        
        logger.info(f"關鍵詞分析完成，找到 {keyword_count} 個關鍵詞，風險評分: {risk_score:.2f}")
        
        return {
            "found_keywords": found_keywords,
            "keyword_count": keyword_count,
            "keyword_density": keyword_density,
            "risk_score": risk_score
        }
    
    @with_error_handling(reraise=True)
    def analyze(self, message_text: str, user_id: Optional[str] = None, 
                chat_history: Optional[List[str]] = None, 
                user_profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        使用本地規則和 agent 分析訊息。
        
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
        logger.info(f"開始分析訊息，用戶ID: {user_id}")
        
        # 檢查輸入
        if not message_text or not isinstance(message_text, str):
            error_msg = "訊息文本必須是非空字串"
            logger.error(error_msg)
            raise DetectionError(error_msg, status_code=400)
        
        # 如果沒有聊天歷史，則只使用當前訊息
        if not chat_history:
            chat_history = [message_text]
        
        try:
            # 步驟 1: 基於關鍵詞的分析
            keyword_result = self._keyword_analysis(message_text)
            
            # 步驟 2: 格式化對話歷史用於 agent 分析
            formatted_conversation = format_conversation(chat_history, format_type="json", user_id=user_id)
            logger.debug(f"格式化的對話歷史: {formatted_conversation}")
            # 步驟 3: 使用 agent 進行深度分析
            agent_result = self.agent(formatted_conversation, user_id)
            
            # TODO: 未來實現基於相似度的檢測
            similarity_score = 0.0  # 佔位符，未來會實現
            
            # 步驟 4: 綜合分析結果 (暫時調整權重，移除相似度分析比重)
            combined_confidence = (
                keyword_result["risk_score"] * 0.4 +  # 關鍵詞分析權重 40%
                agent_result.get("confidence", 0.5) * 0.6  # agent 分析權重 60%
            )
            
            # 判斷最終結果
            risk_level = agent_result.get("risk_level", "低")
            
            # 根據風險級別確定標籤
            if risk_level == "高":
                label = "scam"
            elif risk_level == "中":
                label = "suspicious"
            else:
                label = "safe"
            
            # 構建回應
            reply = agent_result.get("reply", "我已分析了您的訊息，未發現明顯的詐騙跡象。")
            
            # 若是高風險，添加警告
            if label == "scam":
                reply = f"[警告] 這可能是詐騙！\n\n{reply}"
            
            # 記錄結果
            logger.info(f"分析完成，標籤: {label}, 可信度: {combined_confidence:.2f}")
            
            # 返回綜合結果
            return {
                "label": label,
                "confidence": combined_confidence,
                "reply": reply,
                "analysis": {
                    "keyword_analysis": keyword_result,
                    "agent_analysis": agent_result
                }
            }
        except Exception as e:
            error_msg = f"本地檢測過程中發生錯誤: {str(e)}"
            logger.error(error_msg)
            raise DetectionError(error_msg, original_error=e)
