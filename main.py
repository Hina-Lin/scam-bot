#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
詐騙檢測 LINE Bot - 主程式入口點
"""

import os
from dotenv import load_dotenv
from src.api.app import create_app

# 載入環境變數
load_dotenv()

# 創建應用程式
app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
