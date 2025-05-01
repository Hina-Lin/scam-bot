"""
詐騙檢測機器人 - 主要應用程式

這是詐騙檢測機器人應用程式的主要入口點。
它設置了 Flask 應用程式並初始化所有服務和組件。
"""

from flask import Flask
import os

# 導入配置
from config import Config

# 導入工具
from utils.logger import app_logger as logger

# 導入服務
from services.conversation_service import ConversationService
from services.detection_service import DetectionService
from services.storage_service import StorageService

# 導入客戶端
from clients.line_client import LineClient
from clients.analysis_api import AnalysisApiClient

# 導入 API 處理器
from api.line_webhook import line_webhook, LineWebhookHandler

def create_app():
    """
    創建並配置 Flask 應用程式。
    
    Returns:
        Flask: 已配置的 Flask 應用程式
    """
    # 驗證配置
    try:
        Config.validate()
    except ValueError as e:
        logger.error(f"配置錯誤: {e}")
        raise
        
    # 創建 Flask 應用程式
    app = Flask(__name__)
    
    # 初始化客戶端
    line_client = LineClient(Config.LINE_CHANNEL_ACCESS_TOKEN)
    
    # 只有在配置了 URL 時才初始化分析 API 客戶端
    analysis_client = None
    if Config.ANALYSIS_API_URL:
        logger.info(f"使用外部分析 API: {Config.ANALYSIS_API_URL}")
        analysis_client = AnalysisApiClient(Config.ANALYSIS_API_URL)
    else:
        logger.info("使用本地關鍵詞檢測（未配置外部 API）")
    
    # 初始化服務
    detection_service = DetectionService(analysis_client)
    storage_service = StorageService()
    conversation_service = ConversationService(
        detection_service=detection_service,
        storage_service=storage_service,
        line_client=line_client
    )
    
    # 初始化和配置 webhook 處理器
    webhook_handler = LineWebhookHandler(
        conversation_service=conversation_service,
        channel_secret=Config.LINE_CHANNEL_SECRET
    )
    
    # 註冊藍圖
    app.register_blueprint(line_webhook)
    
    # 將 webhook 處理器儲存在藍圖中以供路由訪問
    line_webhook.webhook_handler = webhook_handler
    
    # 首頁路由用於健康檢查
    @app.route("/")
    def index():
        return "詐騙檢測機器人正在執行中!"
    
    return app

# 創建 Flask 應用程式
app = create_app()

# 如果直接執行則運行應用程式
if __name__ == "__main__":
    port = Config.PORT
    debug = Config.DEBUG
    
    logger.info(f"詐騙檢測機器人啟動於埠口 {port} (除錯模式={debug})")
    app.run(host="0.0.0.0", port=port, debug=debug)
