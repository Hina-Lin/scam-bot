"""
LINE Webhook API 處理器

此模組處理來自 LINE 平台的 webhook 請求。
它驗證 webhook 事件並將它們路由到適當的服務。

端點：
- POST /callback: 接收 LINE 平台的 webhook 事件
"""

from typing import Dict, List, Any, Optional
from flask import Blueprint, request, abort, jsonify
import json
from utils.logger import get_api_logger
from utils.error_handler import AppError, LineError, with_error_handling
from services.conversation_service import ConversationService

# 取得模組特定的日誌記錄器
logger = get_api_logger("line_webhook")

# 為 LINE webhook 創建 Flask 藍圖
line_webhook = Blueprint('line_webhook', __name__)

# 對藍圖添加處理器屬性
line_webhook.webhook_handler = None 

# === API 端點定義 ===
@line_webhook.route("/callback", methods=["POST"])
def callback():
    """
    LINE webhook 的 Flask 路由處理器。
    此函數註冊到 Flask 應用程式以處理 webhook 呼叫。
    
    端點: POST /callback
    """
    try:
        # 從 Flask 應用程式上下文獲取處理器
        handler = line_webhook.webhook_handler  # type: LineWebhookHandler
        
        # 處理請求
        body = request.get_data(as_text=True)
        return handler.handle_webhook(body)
    except AppError as e:
        logger.error(f"處理 webhook 時發生應用錯誤: {str(e)}")
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        logger.error(f"處理 webhook 時發生未捕獲錯誤: {str(e)}")
        error = AppError(f"處理 webhook 時發生錯誤: {str(e)}", original_error=e)
        return jsonify(error.to_dict()), 500


class LineWebhookHandler:
    """LINE webhook 事件的處理器。"""
    
    def __init__(self, conversation_service: ConversationService, channel_secret: str):
        """
        初始化 webhook 處理器。
        
        Args:
            conversation_service: 處理對話的服務
            channel_secret: LINE 渠道密鑰用於請求驗證
        """
        self.conversation_service = conversation_service
        self.channel_secret = channel_secret
    
    @with_error_handling(reraise=True)
    def handle_webhook(self, request_data: str) -> str:
        """
        處理來自 LINE 的 webhook 請求。
        
        Args:
            request_data: 請求正文（文本格式）
            
        Returns:
            str: 如果成功則返回 'OK'
            
        Raises:
            LineError: 如果處理過程中發生錯誤
        """
        try:
            # 解析 JSON 請求正文
            json_data = json.loads(request_data)
            
            # 記錄收到的數據
            logger.info("接收到的 webhook 資料")
            
            # 處理 webhook 中的每個事件
            events = json_data.get("events", [])
            if not events:
                logger.warning("收到的 webhook 不包含事件")
                return "OK"
                
            for event in events:
                self._process_event(event)
                
            return "OK"
            
        except json.JSONDecodeError as e:
            error_msg = f"無效的 JSON 格式: {str(e)}"
            logger.error(error_msg)
            raise LineError(error_msg, status_code=400, original_error=e)
        except Exception as e:
            error_msg = f"處理 webhook 時發生錯誤: {str(e)}"
            logger.error(error_msg)
            raise LineError(error_msg, original_error=e)
    
    @with_error_handling(reraise=True)
    def _process_event(self, event: Dict[str, Any]) -> None:
        """
        處理單個 LINE 事件。
        
        Args:
            event: 來自 LINE 的事件數據
            
        Raises:
            LineError: 如果處理過程中發生錯誤
        """
        try:
            # 確認事件格式
            if "type" not in event:
                raise LineError("事件缺少 'type' 字段", status_code=400)
                
            # 只處理訊息事件，其它類型的事件記錄但不處理
            if event["type"] == "message":
                # 基本驗證
                if "replyToken" not in event:
                    raise LineError("訊息事件缺少 'replyToken' 字段", status_code=400)
                if "userId" not in event.get("source", {}):
                    raise LineError("事件來源缺少 'userId' 字段", status_code=400)
                
                # 取出基本訊息
                user_id = event["source"]["userId"]
                reply_token = event["replyToken"]
                message = event["message"]
                
                # 記錄事件
                logger.info(f"收到來自 {user_id} 的 {message['type']} 類型訊息")
                
                # 將整個事件轉發到對話服務，由服務層處理不同類型的訊息
                self.conversation_service.process_event(
                    user_id=user_id,
                    reply_token=reply_token,
                    event_type="message",
                    message=message
                )
            else:
                logger.info(f"收到不支援的事件類型: {event.get('type')}")
                
        except Exception as e:
            error_msg = f"處理事件時發生錯誤: {str(e)}"
            logger.error(error_msg)
            raise LineError(error_msg, original_error=e)
