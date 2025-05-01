"""
LINE API 客戶端

此模組提供與 LINE Messaging API 互動的客戶端。
它處理發送訊息、獲取使用者資料和其他 LINE 特定功能。
"""

import requests
import json
import traceback
from utils.logger import get_client_logger

# 取得模組特定的日誌記錄器
logger = get_client_logger("line")

class LineClient:
    """
    與 LINE API 互動的客戶端。
    """
    
    def __init__(self, channel_access_token):
        """
        初始化 LINE 客戶端。
        
        Args:
            channel_access_token: 用於認證的 LINE 渠道訪問令牌
        """
        self.channel_access_token = channel_access_token
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {channel_access_token}"
        }
    
    def reply_message(self, reply_token, text):
        """
        使用 LINE Messaging API 回覆使用者訊息。
        
        Args:
            reply_token: 來自 webhook 事件的回覆令牌
            text: 要發送的文字訊息
            
        Returns:
            bool: 成功則為 True，否則為 False
        """
        try:
            url = "https://api.line.me/v2/bot/message/reply"
            payload = {
                "replyToken": reply_token,
                "messages": [
                    {
                        "type": "text",
                        "text": text
                    }
                ]
            }
            
            logger.info(f"回覆訊息: {text[:30]}...")
            response = requests.post(
                url, 
                headers=self.headers, 
                data=json.dumps(payload)
            )
            
            if response.status_code == 200:
                logger.info("訊息回覆成功")
                return True
            else:
                logger.error(f"回覆訊息失敗，狀態碼：{response.status_code}, 回覆內容：{response.text}")
                return False
                
        except Exception as e:
            logger.error(f"回覆訊息時發生錯誤: {e}")
            logger.error(traceback.format_exc())
            return False
    
    def get_profile(self, user_id):
        """
        從 LINE 獲取使用者的資料。
        
        Args:
            user_id: LINE 使用者 ID
            
        Returns:
            dict: 使用者資料或如果失敗則為空字典
        """
        try:
            url = f"https://api.line.me/v2/bot/profile/{user_id}"
            
            logger.info(f"獲取使用者 {user_id} 的資料")
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                logger.info("成功獲取使用者資料")
                return response.json()
            else:
                logger.warning(f"獲取使用者資料失敗，狀態碼：{response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"獲取使用者資料時發生錯誤: {e}")
            logger.error(traceback.format_exc())
            return {}
    
    def push_message(self, user_id, text):
        """
        向使用者推送訊息，無需回覆令牌。
        
        Args:
            user_id: 要發送訊息的 LINE 使用者 ID
            text: 要發送的文字訊息
            
        Returns:
            bool: 成功則為 True，否則為 False
        """
        try:
            url = "https://api.line.me/v2/bot/message/push"
            payload = {
                "to": user_id,
                "messages": [
                    {
                        "type": "text",
                        "text": text
                    }
                ]
            }
            
            logger.info(f"向使用者 {user_id} 推送訊息")
            response = requests.post(
                url, 
                headers=self.headers, 
                data=json.dumps(payload)
            )
            
            if response.status_code == 200:
                logger.info("訊息推送成功")
                return True
            else:
                logger.error(f"推送訊息失敗，狀態碼：{response.status_code}, 回覆內容：{response.text}")
                return False
                
        except Exception as e:
            logger.error(f"推送訊息時發生錯誤: {e}")
            logger.error(traceback.format_exc())
            return False
