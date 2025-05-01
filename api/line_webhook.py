"""
LINE Webhook API 處理器

此模組處理來自 LINE 平台的 webhook 請求。
它驗證 webhook 事件並將它們路由到適當的服務。
"""

from flask import Blueprint, request, abort
import json
import traceback
from utils.logger import get_api_logger

# 取得模組特定的日誌記錄器
logger = get_api_logger("line_webhook")

# 為 LINE webhook 創建 Flask 藍圖
line_webhook = Blueprint('line_webhook', __name__)

class LineWebhookHandler:
    """
    LINE webhook 事件的處理器。
    """
    
    def __init__(self, conversation_service, channel_secret):
        """
        初始化 webhook 處理器。
        
        Args:
            conversation_service: 處理對話的服務
            channel_secret: LINE 渠道密鑰用於請求驗證
        """
        self.conversation_service = conversation_service
        self.channel_secret = channel_secret
        
    def handle_webhook(self, request_data):
        """
        處理來自 LINE 的 webhook 請求。
        
        Args:
            request_data: 請求正文（文本格式）
            
        Returns:
            str: 如果成功則返回 'OK'
        """
        try:
            # 解析 JSON 請求正文
            json_data = json.loads(request_data)
            
            # 記錄收到的數據
            logger.info("接收到的 webhook 資料")
            
            # 處理 webhook 中的每個事件
            events = json_data.get("events", [])
            for event in events:
                self._process_event(event)
                
            return "OK"
            
        except Exception as e:
            logger.error(f"處理 webhook 時發生錯誤: {str(e)}")
            logger.error(traceback.format_exc())
            abort(400)
    
    def _process_event(self, event):
        """
        處理單個 LINE 事件。
        
        Args:
            event: 來自 LINE 的事件數據
            
        Returns:
            None
        """
        # 目前僅處理含文本內容的訊息事件
        if event["type"] == "message" and event["message"]["type"] == "text":
            reply_token = event["replyToken"]
            user_msg = event["message"]["text"]
            user_id = event["source"]["userId"]
            
            logger.info(f"收到來自 {user_id} 的訊息: {user_msg}")
            
            # 轉發到對話服務
            self.conversation_service.process_message(
                user_id=user_id, 
                message_text=user_msg, 
                reply_token=reply_token
            )

# Flask 路由處理器
@line_webhook.route("/callback", methods=["POST"])
def callback():
    """
    LINE webhook 的 Flask 路由處理器。
    此函數註冊到 Flask 應用程式以處理 webhook 呼叫。
    """
    # 從 Flask 應用程式上下文獲取處理器
    handler = line_webhook.webhook_handler
    
    # 處理請求
    body = request.get_data(as_text=True)
    return handler.handle_webhook(body)
