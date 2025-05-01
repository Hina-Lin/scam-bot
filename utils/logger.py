"""
日誌工具模組

此模組配置應用程式的日誌系統，支援終端機顯示和檔案記錄兩種模式。
"""

import logging
import os
import sys
from datetime import datetime

# 確保日誌目錄存在
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

class CustomFormatter(logging.Formatter):
    """
    自定義日誌格式化工具，用於終端機輸出
    """
    
    def format(self, record):
        """
        自訂終端機輸出格式： [LEVEL] MODULE, MESSAGE
        
        Args:
            record: 日誌記錄
            
        Returns:
            str: 格式化後的日誌字串
        """
        module = record.name
        level = record.levelname
        message = record.msg
        
        # 如果是 % 格式化，則需要先格式化訊息
        if record.args:
            try:
                message = message % record.args
            except (TypeError, ValueError):
                pass
        
        return f"[{level}] {module}, {message}"

def setup_logger(name, level=logging.INFO, enable_file_log=True):
    """
    設定日誌記錄器，支援終端機和檔案兩種模式
    
    Args:
        name: 日誌記錄器名稱（通常是模組名稱）
        level: 日誌等級（預設：INFO）
        enable_file_log: 是否啟用檔案記錄（預設：是）
        
    Returns:
        logging.Logger: 配置好的日誌記錄器
    """
    # 獲取或建立日誌記錄器
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 避免重複添加處理器
    if logger.handlers:
        return logger
    
    # 終端機處理器（使用自訂格式）
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(CustomFormatter())
    logger.addHandler(console_handler)
    
    # 檔案處理器（帶時間戳記）
    if enable_file_log:
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = os.path.join(LOG_DIR, f'{today}.log')
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger

# 建立應用程式預設日誌記錄器
app_logger = setup_logger("scam_bot")

# 定義一些便利函數來快速建立特定模組的日誌記錄器
def get_api_logger(module_name=None, enable_file_log=True):
    """
    建立 API 層的日誌記錄器
    
    Args:
        module_name: 模組名稱（可選）
        enable_file_log: 是否啟用檔案記錄（預設：是）
        
    Returns:
        logging.Logger: API 層的日誌記錄器
    """
    name = f"api.{module_name}" if module_name else "api"
    return setup_logger(name, enable_file_log=enable_file_log)

def get_service_logger(module_name=None, enable_file_log=True):
    """
    建立服務層的日誌記錄器
    
    Args:
        module_name: 模組名稱（可選）
        enable_file_log: 是否啟用檔案記錄（預設：是）
        
    Returns:
        logging.Logger: 服務層的日誌記錄器
    """
    name = f"services.{module_name}" if module_name else "services"
    return setup_logger(name, enable_file_log=enable_file_log)

def get_client_logger(module_name=None, enable_file_log=True):
    """
    建立客戶端層的日誌記錄器
    
    Args:
        module_name: 模組名稱（可選）
        enable_file_log: 是否啟用檔案記錄（預設：是）
        
    Returns:
        logging.Logger: 客戶端層的日誌記錄器
    """
    name = f"clients.{module_name}" if module_name else "clients"
    return setup_logger(name, enable_file_log=enable_file_log)
