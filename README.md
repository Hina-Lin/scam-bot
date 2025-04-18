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

## 資料流程圖（可日後加圖）

```text
使用者 → LINE Bot → Flask Server → 送出 JSON → 分析 API → 回傳風險標記 → 回覆訊息（含警告）
```

---

## 分析資料格式（送出給 API）

系統會將使用者資訊與對話資料整理成以下格式：

| 欄位名稱         | 資料型別         | 說明                                    |
|------------------|------------------|-----------------------------------------|
| `user_id`        | string           | LINE 使用者的唯一 ID                     |
| `display_name`   | string           | 使用者顯示名稱，可為空字串              |
| `picture_url`    | string           | 使用者頭像圖片連結，可為空字串          |
| `language`       | string           | 使用者語言設定（範例：zh-Hant、en）     |
| `current_message`| string           | 使用者此輪傳送的訊息                    |
| `chat_history`   | list of strings  | 此使用者過去的對話紀錄，依序儲存為陣列 |

### 範例 JSON：

```json
{
  "user_id": "Uxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "display_name": "使用者名稱",
  "picture_url": "https://example.com/profile.jpg",
  "language": "zh-Hant",
  "current_message": "最近我對投資有點興趣",
  "chat_history": [
    "你好呀！",
    "你平常都做什麼工作？",
    "你看起來很專業欸",
    "我最近對理財有點好奇",
    "最近我對投資有點興趣"
  ]
}
```

---

## 使用方式

1. 複製專案到本地
2. 建立虛擬環境並安裝套件：
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. 執行伺服器
   ```bash
   python app.py
   ```
4. 開啟 ngrok 並設定 Webhook（或使用 Render）

---

## 技術與工具

- Python + Flask
- LINE Messaging API
- Ngrok / Render 雲端部署
- 模型串接（尚未串接）

---

## 測試方式（目前尚未串接模型）

加 LINE Bot 好友測試訊息回覆  
https://line.me/R/ti/p/@572bgqwq

目前使用簡單關鍵字模擬分析結果：  
（之後會換成串接 API）

```python
def analyze_text(text):
    scam_keywords = [
        "怎麼投資", "怎麼給你", "錢怎麼轉",
        "要匯到哪", "我相信你", "我沒有別人可以相信了"
    ]
    if any(word in text for word in scam_keywords):
        return {
            "label": "scam",
            "confidence": 0.9,
            "reply": "這是我投資成功的故事，你想聽嗎？"
        }
    else:
        return {
            "label": "safe",
            "confidence": 0.1,
            "reply": "哈哈你說得真有趣，我懂你！"
        }
