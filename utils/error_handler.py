"""
錯誤處理工具

提供統一的錯誤處理機制，包括錯誤記錄、分類和格式化。
"""

import traceback
from enum import Enum
from utils.logger import get_service_logger

# 取得模組特定的日誌記錄器
logger = get_service_logger("error_handler")

# === 錯誤類型枚舉 ===
class ErrorType(Enum):
    """錯誤類型枚舉，用於分類不同來源的錯誤"""
    UNKNOWN = "unknown"
    API = "api"
    DATABASE = "database"
    LINE = "line"
    DETECTION = "detection"
    AUTH = "auth"
    VALIDATION = "validation"
    CONFIG = "config"

# === 自定義應用程式錯誤類 ===
class AppError(Exception):
    """
    應用程式錯誤基類
    
    提供統一的錯誤格式和分類機制，方便在不同層級間傳遞錯誤訊息。
    """
    
    def __init__(self, message, error_type=ErrorType.UNKNOWN, status_code=500, original_error=None):
        """
        初始化應用程式錯誤
        
        Args:
            message: 錯誤訊息
            error_type: 錯誤類型
            status_code: HTTP 狀態碼（用於 API 回應）
            original_error: 原始異常（如果有）
        """
        self.message = message
        self.error_type = error_type
        self.status_code = status_code
        self.original_error = original_error
        super().__init__(self.message)
    
    def __str__(self):
        """字串表示，用於日誌和錯誤訊息"""
        return f"[{self.error_type.value.upper()}] {self.message}"
    
    def to_dict(self):
        """
        轉換為字典，用於 JSON 回應
        
        Returns:
            dict: 包含錯誤詳情的字典
        """
        error_dict = {
            "error": True,
            "type": self.error_type.value,
            "message": self.message,
            "status_code": self.status_code
        }
        
        # 只在開發環境中包含原始錯誤訊息
        # TODO: 根據環境變數決定是否包含堆疊資訊
        if self.original_error:
            error_dict["original_error"] = str(self.original_error)
        
        return error_dict

# === 特定錯誤類型 ===
class ApiError(AppError):
    """API 錯誤，通常是調用外部 API 時發生"""
    
    def __init__(self, message, status_code=500, original_error=None):
        super().__init__(message, ErrorType.API, status_code, original_error)

class DetectionError(AppError):
    """檢測過程中的錯誤"""
    
    def __init__(self, message, status_code=500, original_error=None):
        super().__init__(message, ErrorType.DETECTION, status_code, original_error)

class LineError(AppError):
    """LINE API 錯誤"""
    
    def __init__(self, message, status_code=500, original_error=None):
        super().__init__(message, ErrorType.LINE, status_code, original_error)

class ValidationError(AppError):
    """數據驗證錯誤"""
    
    def __init__(self, message, status_code=400, original_error=None):
        super().__init__(message, ErrorType.VALIDATION, status_code, original_error)

class ConfigError(AppError):
    """配置錯誤"""
    
    def __init__(self, message, status_code=500, original_error=None):
        super().__init__(message, ErrorType.CONFIG, status_code, original_error)

# === 錯誤處理函數 ===
def handle_error(error, reraise=True):
    """
    統一的錯誤處理函數
    
    記錄錯誤，並根據需要重新拋出或轉換錯誤類型。
    
    Args:
        error: 原始錯誤
        reraise: 是否重新拋出錯誤
    
    Returns:
        AppError: 如果 reraise=False，返回適當的 AppError 實例
    
    Raises:
        AppError: 如果 reraise=True，拋出適當的 AppError 實例
    """
    # 如果已經是 AppError，直接使用
    if isinstance(error, AppError):
        app_error = error
    else:
        # 根據異常類型選擇適當的 AppError 子類
        error_message = str(error)
        if "api" in error_message.lower() or "request" in error_message.lower():
            app_error = ApiError(f"API 錯誤: {error_message}", original_error=error)
        elif "line" in error_message.lower():
            app_error = LineError(f"LINE 錯誤: {error_message}", original_error=error)
        elif "detection" in error_message.lower() or "analyze" in error_message.lower():
            app_error = DetectionError(f"檢測錯誤: {error_message}", original_error=error)
        elif "validation" in error_message.lower() or "invalid" in error_message.lower():
            app_error = ValidationError(f"驗證錯誤: {error_message}", original_error=error)
        elif "config" in error_message.lower() or "setting" in error_message.lower():
            app_error = ConfigError(f"配置錯誤: {error_message}", original_error=error)
        else:
            app_error = AppError(f"未知錯誤: {error_message}", original_error=error)
    
    # 記錄錯誤訊息
    logger.error(str(app_error))
    
    # 記錄完整的堆疊跟蹤
    logger.error(traceback.format_exc())
    
    # 根據需要重新拋出或返回錯誤
    if reraise:
        raise app_error
    return app_error

# === 裝飾器：為函數添加錯誤處理 ===
def with_error_handling(reraise=True):
    """
    錯誤處理裝飾器，可以應用於任何函數
    
    Args:
        reraise: 是否重新拋出錯誤
    
    Returns:
        裝飾器函數
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                return handle_error(e, reraise)
        return wrapper
    return decorator
