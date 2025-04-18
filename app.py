from flask import Flask, request, abort
import json
import requests
import logging
import traceback


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


app = Flask(__name__)

# === LINE Bot 憑證資訊 ===
CHANNEL_ACCESS_TOKEN = "cb4k7eDRiCopTS7yegkIq0KLt+n+4tKbTZFlANL8lYaFmMQD6IUjIq17GMPvut+7U4vchoFiTgoLEmYt1Fa4ZpQncZgb00eItntfJ9VHkM+0HQkn6V1PRxSrH0mBxHQr+D9K9J7cml6xExVQuRN70gdB04t89/1O/w1cDnyilFU="
CHANNEL_SECRET = "fb253dc72c8c3f018d1f814ed0833318"

# === 模擬詐騙分析結果 ===
def analyze_text(text):
    scam_keywords = [
    "怎麼投資", "怎麼給你", "錢怎麼轉", 
    "要匯到哪", "我相信你", "我沒有別人可以相信了"]

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

# === 傳送資料到 API 伺服器並接收回覆語句 + 詐騙風險分析 ===
def send_to_api(data):
    try:
        api_url = "https://example.com/api/analyze"  # 替換成正式 API URL
        headers = {"Content-Type": "application/json"}
        res = requests.post(api_url, headers=headers, data=json.dumps(data), timeout=5)
        if res.status_code == 200:
            print(res.json())  # 印出回傳內容方便 debug
            return res.json()
        else:
            print(f"API 回應錯誤：{res.status_code}")
            return {"label": "unknown", "confidence": 0.0, "reply": "目前系統繁忙，請稍後再試。"}
    except Exception as e:
        print(f"傳送 API 發生錯誤：{e}")
        return {"label": "unknown", "confidence": 0.0, "reply": "目前系統無法使用，請晚點再聊。"}

# 回傳生成的詐騙訊息
def generate_reply(result):
    return result.get("reply", "我還想聽更多～")

# 判斷是否需要警示訊息
def should_warn(result):
    return result.get("label") == "scam" and result.get("confidence", 0.0) > 0.7

# 如果需要警示，產生警示內容
def generate_warning(result):
    confidence = result.get("confidence", 0.0)
    return f"[警示] 你可能正被詐騙，請提高警覺（可信度 {confidence * 100:.1f}%）"

# === 獲取使用者基本資料 ===
def get_user_profile(user_id):
    try:
        url = f"https://api.line.me/v2/bot/profile/{user_id}"
        headers = {
            "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"
        }
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            return res.json()
        else:
            logging.warning(f"取得使用者資料失敗，狀態碼：{res.status_code}")
    except Exception as e:
        logging.error("[get_user_profile 錯誤]")
        logging.error(traceback.format_exc())
    return {}  


# === 整合資料給模型 / API 使用 ===
def prepare_analysis_data(user_id, message):
    profile = get_user_profile(user_id)
    history = user_chat_history.get(user_id, [])
    return {
        "user_id": user_id,
        "display_name": profile.get("displayName", ""),
        "picture_url": profile.get("pictureUrl", ""),
        "language": profile.get("language", ""),
        "current_message": message,
        "chat_history": history
    }

# === 儲存聊天紀錄（記憶體版） ===
user_chat_history = {}  # key: userId, value: list of text messages

# === 接收來自 LINE 的訊息 ===
@app.route("/callback", methods=["POST"])
def callback():
    body = request.get_data(as_text=True)

    try:
        json_data = json.loads(body)
        logging.info("\n==== [Log] 接收到的資料 ====\n" + json.dumps(json_data, ensure_ascii=False, indent=2))


        events = json_data.get("events", [])
        for event in events:
            if event["type"] == "message" and event["message"]["type"] == "text":
                reply_token = event["replyToken"]
                user_msg = event["message"]["text"]
                user_id = event["source"]["userId"]

                # 儲存聊天紀錄
                user_chat_history.setdefault(user_id, []).append(user_msg)

                # 準備分析資料（模擬送出）
                analysis_data = prepare_analysis_data(user_id, user_msg)
                logging.info("\n==== [Log] 準備送出的分析資料 ====\n" + json.dumps(analysis_data, ensure_ascii=False, indent=2))


                # 分析結果
                # result = send_to_api(analysis_data)  # 真實分析結果
                result = analyze_text(user_msg)  # 模擬分析

                reply_msg = generate_reply(result)
                if should_warn(result):
                    reply_msg += "\n" + generate_warning(result)

                reply_to_user(reply_token, reply_msg)

    except Exception as e:
        logging.error("\n==== [Log] 發生錯誤 ====")
        logging.error(str(e))
        logging.error(traceback.format_exc())  
        abort(400)



    return "OK"

# === 回傳訊息給使用者（使用 reply API） ===
def reply_to_user(reply_token, text):
    try:
        url = "https://api.line.me/v2/bot/message/reply"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"
        }
        payload = {
            "replyToken": reply_token,
            "messages": [
                {
                    "type": "text",
                    "text": text
                }
            ]
        }
        res = requests.post(url, headers=headers, data=json.dumps(payload))
        if res.status_code != 200:
            logging.warning(f"回傳訊息失敗，狀態碼：{res.status_code}, 回傳內容：{res.text}")
    except Exception as e:
        logging.error("[reply_to_user 錯誤]")
        logging.error(traceback.format_exc())


# === 測試首頁 ===
@app.route("/")
def index():
    return "Hello, Scam Bot!"

if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
