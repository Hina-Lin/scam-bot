"""
對話服務 - 應用服務層

此服務協調使用者與系統之間的對話流程。
它負責編排詐騙檢測和生成適當的回應。
"""

from typing import Dict, List, Any, Optional, Union
from utils.logger import get_service_logger
from utils.error_handler import AppError, with_error_handling, DetectionError
from services.domain.detection_service import DetectionService
from services.domain.storage_service import StorageService
from clients.line_client import LineClient

# 取得模組特定的日誌記錄器
logger = get_service_logger("conversation")

# === 主要入口點 ===
class ConversationService:
    """應用服務，管理對話流程，協調檢測和回應生成"""
    
    def __init__(self, 
                 detection_service: DetectionService, 
                 storage_service: StorageService, 
                 line_client: LineClient):
        """
        初始化對話服務及其依賴項。
        
        Args:
            detection_service: 檢測訊息中詐騙的服務
            storage_service: 儲存對話歷史的服務
            line_client: 與 LINE API 互動的客戶端
        """
        self.detection_service = detection_service
        self.storage_service = storage_service
        self.line_client = line_client
    
    @with_error_handling(reraise=True)
    def process_event(self, 
                      user_id: str, 
                      reply_token: str, 
                      event_type: str, 
                      message: Dict[str, Any]) -> None:
        """
        處理來自 LINE 的各種事件。
        
        Args:
            user_id: 發送訊息的使用者 ID
            reply_token: 用於回覆此訊息的令牌
            event_type: 事件類型（例如："message"）
            message: 完整的訊息物件
            
        Raises:
            AppError: 如果處理過程中發生錯誤
        """
        try:
            message_type = message.get("type")
            
            # 根據不同的訊息類型進行處理
            if message_type == "text":
                # 處理文字訊息
                if "text" not in message:
                    raise AppError("文本訊息缺少 'text' 字段")
                
                message_text = message["text"]
                logger.info(f"處理來自 {user_id} 的文字訊息: {message_text}")
                
                # 呼叫原有的文字訊息處理方法
                self.process_message(user_id, message_text, reply_token)
                
            elif message_type == "image":
                # 處理圖片訊息
                image_id = message.get("id")
                if not image_id:
                    raise AppError("圖片訊息缺少 'id' 字段")
                
                logger.info(f"處理來自 {user_id} 的圖片，ID: {image_id}")
                
                # TODO: 實現圖片處理邏輯
                # 暫時回覆用戶圖片已收到但尚未實現分析功能
                response = "我已收到您的圖片，但目前還無法分析圖片內容。請以文字方式提供您想要檢測的訊息。"
                self.line_client.reply_message(reply_token, response)
                
            elif message_type == "file":
                # 處理檔案訊息
                file_id = message.get("id")
                file_name = message.get("fileName", "未知檔案")
                file_size = message.get("fileSize", 0)
                
                logger.info(f"處理來自 {user_id} 的檔案: {file_name} ({file_size} bytes), ID: {file_id}")
                
                # TODO: 實現檔案處理邏輯
                # 暫時回覆用戶檔案已收到但尚未實現分析功能
                response = f"我已收到您的檔案 {file_name}，但檔案處理功能尚未實現。請以文字方式提供您想要檢測的訊息。"
                self.line_client.reply_message(reply_token, response)
                
            else:
                # 其他未支援的訊息類型
                logger.info(f"收到不支援的訊息類型: {message_type}")
                response = "很抱歉，我無法處理這種類型的訊息。請以文字方式提供您想要檢測的訊息。"
                self.line_client.reply_message(reply_token, response)
                
        except Exception as e:
            error_msg = f"處理事件時發生錯誤: {str(e)}"
            logger.error(error_msg)
            
            # 嘗試發送錯誤訊息給使用者
            try:
                error_response = "很抱歉，處理您的訊息時發生問題。請稍後再試。"
                self.line_client.reply_message(reply_token, error_response)
            except Exception as reply_error:
                logger.error(f"無法發送錯誤回應: {str(reply_error)}")
            
            # 重新拋出異常
            raise AppError(error_msg, original_error=e)
            
    @with_error_handling(reraise=True)
    def process_message(self, user_id: str, message_text: str, reply_token: str) -> None:
        """
        處理來自使用者的文字訊息。
        
        Args:
            user_id: 發送訊息的使用者 ID
            message_text: 訊息的文字內容
            reply_token: 用於回覆此訊息的令牌
            
        Raises:
            AppError: 如果處理過程中發生錯誤
        """
        try:
            # 將訊息儲存在歷史記錄中
            self.storage_service.add_message(user_id, message_text)
            
            # 獲取使用者的聊天歷史
            history = self.storage_service.get_chat_history(user_id)
            
            # 如果需要，獲取使用者資料
            user_profile = self.line_client.get_profile(user_id)
            
            # 對訊息進行詐騙檢測分析
            logger.info(f"分析來自 {user_id} 的訊息")
            
            try:
                detection_result = self.detection_service.analyze_message(
                    message_text, 
                    user_id,
                    history,
                    user_profile
                )
            except Exception as e:
                # 如果檢測失敗，使用預設安全回應
                logger.error(f"檢測失敗，使用預設回應: {str(e)}")
                detection_result = {
                    "label": "unknown",
                    "confidence": 0.0,
                    "reply": "很抱歉，我暫時無法處理您的訊息。請稍後再試。"
                }
            
            # 根據檢測結果生成適當的回應
            response = self._generate_response(detection_result)
            
            # 將回應發送回使用者
            logger.info(f"回覆給 {user_id}")
            self.line_client.reply_message(reply_token, response)
            
        except Exception as e:
            error_msg = f"處理文字訊息時發生錯誤: {str(e)}"
            logger.error(error_msg)
            raise AppError(error_msg, original_error=e)

    # === 輔助方法 ===
    def _generate_response(self, detection_result: Dict[str, Any]) -> str:
        """
        根據檢測結果生成回應。
        
        Args:
            detection_result: 詐騙檢測分析的結果
            
        Returns:
            str: 要發送給使用者的回應文字
        """
        # 從檢測結果中獲取基本回應
        reply = detection_result.get("reply", "")
        
        # 如果可能是詐騙，添加警告
        if detection_result.get("label") == "scam" and detection_result.get("confidence", 0) > 0.7:
            confidence = detection_result.get("confidence", 0)
            warning = f"[警示] 您可能正被詐騙，請提高警覺（可信度 {confidence * 100:.1f}%）"
            reply = f"{reply}\n{warning}"
            logger.warning(f"偵測到詐騙訊息，可信度: {confidence * 100:.1f}%")
        else:
            logger.info(f"訊息被標記為: {detection_result.get('label', 'unknown')}")
            
        return reply
