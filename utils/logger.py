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
    並依照日誌級別顯示不同顏色
    """
    
    # 定義顏色代碼
    COLORS = {
        'DEBUG': '\033[94m',      # 淡藍色
        'INFO': '\033[92m',       # 綠色
        'WARNING': '\033[93m',    # 黃色
        'ERROR': '\033[91m',      # 紅色
        'CRITICAL': '\033[1;91m'  # 粗體紅色
    }
    RESET = '\033[0m'             # 重置顏色
    
    def format(self, record):
        """
        自訂終端機輸出格式，依照級別顯示不同顏色
        
        Args:
            record: 日誌記錄
            
        Returns:
            str: 格式化後的日誌字串
        """
        # 取得級別和模組名稱
        level_name = record.levelname
        color = self.COLORS.get(level_name, self.RESET)
        
        # 取得模組名稱並簡化顯示
        module = record.name
        # 移除主資料夾前綴，進行簡化顯示
        if '.' in module:
            module = module.split('.')[-1]  # 只取最後一部分
        
        # 取得訊息
        message = record.msg
        
        # 如果是 % 格式化，則需要先格式化訊息
        if record.args:
            try:
                message = message % record.args
            except (TypeError, ValueError):
                pass
        
        # 建立帶顏色的格式化訊息
        return f"{color}[• {level_name}]{self.RESET} [{module}] {message}"

def setup_logger(name, level=logging.INFO, enable_file_log=False):
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
# 使用更直覺的命名方式
def get_api_logger(module_name=None, enable_file_log=False):
    if module_name:
        name = f"api/{module_name}"
    else:
        name = "api"
    return setup_logger(name, enable_file_log=enable_file_log)

def get_service_logger(module_name=None, enable_file_log=False):
    if module_name:
        name = f"services/{module_name}"
    else:
        name = "services"
    return setup_logger(name, enable_file_log=enable_file_log)

def get_client_logger(module_name=None, enable_file_log=False):
    if module_name:
        name = f"clients/{module_name}"
    else:
        name = "clients"
    return setup_logger(name, enable_file_log=enable_file_log)

def get_utils_logger(module_name=None, enable_file_log=False):
    if module_name:
        name = f"utils/{module_name}"
    else:
        name = "utils"
    return setup_logger(name, enable_file_log=enable_file_log)

def get_adk_logger(module_name=None, enable_file_log=False):
    if module_name:
        name = f"adk/{module_name}"
    else:
        name = "adk"
    return setup_logger(name, enable_file_log=enable_file_log)
