# 情感詐騙偵測對話系統

這是一個結合 LINE Bot 與詐騙語句分析的對話型系統，目標是建立一個能模擬詐騙者角色、蒐集對話資訊、分析使用者受騙風險並主動警告的防詐系統。

---

## 專案目標

- 由 LINE Bot 與使用者進行對話
- 模擬詐騙者話術，透過生成模型回應使用者
- 分析使用者對話內容與個資，判斷其受騙傾向
- 適時跳出警示訊息提醒使用者風險

---

## 系統架構

1. 使用 LINE Bot 作為與使用者互動的前端平台
2. 部署於 Render（暫時可用 ngrok 本地測試）
3. Flask 構建後端 API，處理 webhook 請求
4. 將訊息與使用者資料整理為 JSON，送至後端分析模型
5. 分析結果由 API 回傳，系統根據回傳決定回覆語句與是否發出警告

---

## 目錄結構（含第二層）

```
.
├── app.py                    # 入口腳本，啟動 Flask 伺服器
├── config.py                 # 環境設定與環境變數讀取
├── Procfile                  # 部署平台進程設定 (Render/Heroku)
├── api/                      # Webhook 處理路由
│   ├── __init__.py
│   └── line_webhook.py       # 處理 LINE Webhook 請求
├── clients/                  # 封裝外部 API 客戶端 (LINE、分析 API)
│   ├── __init__.py
│   ├── analysis_api.py
│   └── line_client.py
├── data/                     # 詐騙範本資料與階段定義
│   ├── scam_data.json
│   └── stage_definitions.json
├── services/                 # 核心業務邏輯 (對話管理、檢測策略)
│   ├── __init__.py
│   ├── conversation_service.py
│   └── domain/
│       ├── __init__.py
│       ├── storage_service.py
│       └── detection/
│           ├── base.py
│           ├── detection_service.py
│           ├── local_detection.py
│           └── api_detection.py
├── utils/                    # 共用工具 (日誌、錯誤處理、驗證、代理工廠)
│   ├── __init__.py
│   ├── error_handler.py
│   ├── logger.py
│   ├── validator.py
│   └── agents/
│       └── agent_factory.py
├── tests/                    # 測試案例
├── requirements.txt
└── README.md
```

---

## 環境變數配置
請在專案根目錄建立 `.env` 檔案或參考 `.env.sample`，設定以下變數：

- LINE_CHANNEL_SECRET: LINE Bot 的 Channel Secret
- LINE_CHANNEL_ACCESS_TOKEN: LINE Bot 的 Channel Access Token
- ANALYSIS_API_URL: 外部詐騙分析 API 位址（留空則使用本地檢測策略）
- OPENAI_API_KEY / GOOGLE_API_KEY / OPENROUTER_API_KEY: 選用的 LLM 提供商 API 金鑰
- LLM_PROVIDER: LLM 提供商 (openai, gemini, openrouter)
- LLM_MODEL: 選擇的模型名稱
- PORT: 伺服器埠號 (預設 10000)
- DEBUG: 除錯模式 (True/False)

---

## 資料流程圖（可日後加圖）
```text
使用者 (匯出 LINE 對話紀錄)
  ↓
LINE Webhook (api/line_webhook.py)
  ↓
LINE Client 獲取使用者資料 (clients/line_client.py)
  ↓
Conversation Service 處理對話 (services/conversation_service.py)
  ↓
檢測策略選擇
  ├─ LocalDetectionStrategy (services/domain/detection/local_detection.py)
  └─ ApiDetectionStrategy (clients/analysis_api.py)
  ↓
Detection Service 分析整合 (services/domain/detection/detection_service.py)
  ↓
回傳分析結果給 Conversation Service
  ↓
LINE Client 發送回覆消息 (clients/line_client.py)
  ↓
使用者 接收回覆
```

---

## 使用者輸入格式限制
- 僅允許 LINE 匯出對話紀錄內容作為輸入，範例：

```text
2025.04.22 星期二
21:48 USER_A USER_A 已加入群組。
21:48 USER_B USER_B 已加入群組。
21:49 USER_B https://docs.google.com/...
21:51 USER_B 我晚點會先用gpt生個草稿貼上去
21:51 USER_B 你們如果有想修的地方 或是大改都可以直接講～
21:58 USER_C 要不要
21:58 USER_C 不用做簡報
====
```

- 系統實際接收訊息範例（已匿名化）：

```text
[• INFO] [api/line_webhook] 接收到的 webhook 資料: {
  "destination": "DEST_ID",
  "events": [
    {
      "type": "message",
      "message": {
        "type": "text",
        "id": "MSG_ID",
        "text": "2025.04.22 星期二\n21:48 USER_A USER_A 已加入群組。\n...",
      },
      "source": {
        "type": "user",
        "userId": "USER_ID"
      },
      ...
    }
  ]
}
```

---

## 使用方式

1. 複製專案到本地
2. 建立虛擬環境並安裝套件：
   ```bash
   python -m venv venv
   .\venv\Scripts\activate    # Windows
   pip install -r requirements.txt
   ```
3. 配置環境變數：
   ```bash
   copy .env.sample .env        # 並編輯 .env
   ```
4. 執行伺服器：
   ```bash
   python app.py
   ```
   - 本地檢測：若 `ANALYSIS_API_URL` 未設定，系統將使用 `LocalDetectionStrategy`（關鍵詞+Agent分析）
   - 外部 API 檢測：設定 `ANALYSIS_API_URL` 後，系統將呼叫外部分析 API
5. (可選) 運行測試：
   ```bash
   pytest
   ```

---

## 技術與工具

- Python + Flask
- LINE Messaging API
- Ngrok / Render 雲端部署
- 模型串接（目前使用 Google ADK / LiteLLM）

---

## 測試方式

加 LINE Bot 好友測試訊息回覆
https://line.me/R/ti/p/@572bgqwq

---

## 常見問題 (Common Issues)

### 1. `UnicodeDecodeError: 'cp950' codec can't decode byte...`

**錯誤訊息範例:**

```
Traceback (most recent call last):
  ...
  File "C:\Users\User\Desktop\scam-bot\venv\lib\site-packages\litellm\litellm_core_utils\llm_cost_calc\utils.py", line 9, in <module>
    from litellm.utils import get_model_info
  File "C:\Users\User\Desktop\scam-bot\venv\lib\site-packages\litellm\utils.py", line 188, in <module>
    json_data = json.load(f)
  File "C:\Users\User\anaconda3\lib\json\__init__.py", line 293, in load
    return loads(fp.read(),
UnicodeDecodeError: 'cp950' codec can't decode byte 0xc3 in position 1970: illegal multibyte sequence
```

**原因:**

`litellm` 套件在讀取內部 JSON 檔案時，沒有指定 UTF-8 編碼，導致在某些系統環境下（例如預設編碼為 CP950 的繁體中文 Windows）讀取失敗。

**解決方法:**

修改 `litellm` 套件的原始碼，明確指定使用 UTF-8 編碼讀取檔案。

找到檔案： `[你的虛擬環境路徑]\Lib\site-packages\litellm\utils.py`
(例如： `venv\Lib\site-packages\litellm\utils.py`)

將第 187-188 行附近的程式碼：

```python
# 原本的程式碼
with open(file_path, 'r') as f:
    json_data = json.load(f)
```

修改為：

```python
# 修改後的程式碼
with open(file_path, 'r', encoding='utf-8') as f:
    json_data = json.load(f)
```

**注意:** 修改套件原始碼是暫時的解決方法。如果 `litellm` 更新，此修改可能會被覆蓋。建議關注 `litellm` 的官方更新或提出 Issue.

---

## 範例輸入 (Logs)
```text
[• INFO] [api/line_webhook] 接收到的 webhook 資料: {...略...}
[• INFO] [api/line_webhook] 收到來自 USER_ID 的 text 類型訊息
[• INFO] [services/conversation] 處理來自 USER_ID 的文字訊息: 2025.04.22 ...
[• DEBUG] [services/local_detection] 開始分析訊息，用戶ID: USER_ID
...後續日誌略...
```

## 範例輸出 (Response)
```json
[
  {
    "user_name": "USER_A",
    "risk_level": "低",
    "confidence": 1.0,
    "brief_analysis": "使用者僅加入群組，無法判斷意圖，風險低。",
    "evidence": "無詐騙階段跡象。",
    "reply": "USER_A 僅加入群組，未參與對話。基於目前資訊與對話性質，風險低。"
  },
  {
    "user_name": "USER_B",
    "risk_level": "低",
    "confidence": 1.0,
    "brief_analysis": "分享文件連結並提及 AI 協作，符合正常協作情境。",
    "evidence": "無詐騙階段跡象。對話符合協作目的。",
    "reply": "USER_B 的行為符合正常群組協作，未發現詐騙指標，風險低。"
  },
  {
    "user_name": "USER_C",
    "risk_level": "低",
    "confidence": 1.0,
    "brief_analysis": "提出任務建議與格式討論，行為正常，無可疑行為。",
    "evidence": "無詐騙階段跡象。對話符合協作任務。",
    "reply": "USER_C 的建議符合協作需求，未見詐騙指標，風險低。"
  }
]
```
