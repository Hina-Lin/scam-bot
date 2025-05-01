# 詐騙檢測 LINE 機器人

這是一個透過 LINE 機器人作為前端，用於檢測潛在詐騙訊息的 MVP 專案。機器人會分析用戶發送的訊息，如果判定為可能的詐騙，會向用戶發出警告。

## 功能概述

- 透過 LINE Bot 接收使用者訊息
- 使用多種策略分析訊息中的詐騙風險
- 支援外部 API 分析或本地規則檢測
- 向使用者發送適當的回應和警告

## 系統架構

項目採用簡化版的分層架構，主要分為以下幾層：

### API 層 (api/)
處理外部請求的入口點：
- `line_webhook.py`: 處理來自 LINE 平台的 webhook 請求

### 服務層 (services/)
包含核心業務邏輯：
- `conversation_service.py`: 應用服務，協調整個對話流程
- `detection_service.py`: 詐騙檢測服務，選擇合適的檢測策略
- `storage_service.py`: 儲存服務，管理對話歷史
- `domain/`: 包含領域模型和檢測策略實現
  - `detection_strategy.py`: 檢測策略抽象介面
  - `api_detection.py`: 外部 API 檢測策略
  - `local_detection.py`: 本地規則檢測策略

### 客戶端層 (clients/)
負責與外部系統通訊：
- `line_client.py`: 與 LINE API 通訊的客戶端
- `analysis_api.py`: 與外部分析 API 通訊的客戶端

### 工具層 (utils/)
提供通用工具功能：
- `logger.py`: 日誌工具，支援終端機和檔案輸出
- `error_handler.py`: 統一的錯誤處理機制

## 檢測策略

系統支援兩種檢測策略：

1. **API 檢測策略**：使用外部 API 進行詐騙分析
2. **本地規則檢測**：基於本地規則（未來將實現 cosine 相似度計算和 agent 整合）

系統會根據配置自動選擇合適的策略。

## 配置說明

在 `.env` 文件中配置以下環境變數：

```
# LINE Bot 配置
LINE_CHANNEL_SECRET=your_channel_secret_here
LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token_here

# 外部分析 API (可選)
# 如果未設置，將使用本地規則檢測
ANALYSIS_API_URL=

# 伺服器配置
PORT=10000
DEBUG=True
```

## 錯誤處理

系統實現了統一的錯誤處理機制：
- 使用自定義錯誤類型分類不同來源的錯誤
- 提供錯誤處理裝飾器簡化錯誤處理
- 在 API 層統一捕獲和格式化錯誤回應

## 日誌系統

系統支援兩種日誌模式：
- **終端機模式**：顯示為 `[LEVEL] MODULE, MESSAGE`
- **檔案模式**：寫入到 `logs/` 目錄，包含時間戳記

## 開發待辦事項

- [ ] 實現本地檢測策略的 cosine 相似度計算
- [ ] 實現本地檢測策略的 agent 整合
- [ ] 添加單元測試和整合測試
- [ ] 優化監控和日誌機制
- [ ] 添加更多的詐騙檢測規則
- [ ] 提供更具體的警告訊息

## 安裝與執行

1. 安裝依賴套件：
   ```
   pip install -r requirements.txt
   ```

2. 配置環境變數（編輯 `.env` 文件）

3. 運行應用程式：
   ```
   python app.py
   ```

4. 設定 LINE Bot Webhook URL 為：
   ```
   https://your-domain.com/callback
   ```

## 專案結構

```
scam-bot/
├── api/                     # API 層
│   └── line_webhook.py      # LINE webhook 處理
│
├── services/                # 服務層
│   ├── domain/              # 領域模型和策略
│   │   ├── api_detection.py      # API 檢測策略
│   │   ├── detection_strategy.py # 抽象策略介面
│   │   └── local_detection.py    # 本地檢測策略
│   │
│   ├── conversation_service.py # 應用服務
│   ├── detection_service.py    # 檢測服務
│   └── storage_service.py      # 儲存服務
│
├── clients/                 # 客戶端層
│   ├── analysis_api.py      # 外部分析 API 客戶端
│   └── line_client.py       # LINE API 客戶端
│
├── utils/                   # 工具函數
│   ├── error_handler.py     # 錯誤處理工具
│   └── logger.py            # 日誌工具
│
├── logs/                    # 日誌目錄
│
├── app.py                   # 主程式入口點
├── config.py                # 配置處理
├── .env                     # 環境變數
├── .env.sample              # 環境變數範例
└── requirements.txt         # 依賴套件
```

## 注意事項

- 這是一個 MVP 階段的專案，仍在持續開發中
- 目前的本地檢測策略是一個佔位實現，將在未來版本中完善
- 此專案僅用於演示和教育目的，不應用於實際的詐騙檢測系統