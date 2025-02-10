from flask import Flask, request
from flask_socketio import SocketIO, emit
from speech_to_text import record_and_transcribe
from flask_cors import CORS
import os
import tempfile
import base64


app = Flask(__name__)
CORS(app)  # 解決 CORS 問題
socketio = SocketIO(app, cors_allowed_origins="*")  # 啟用 WebSocket

@app.route("/")
def index():
    return "WebSocket Server is running!"

import os
import base64
import tempfile
import json
from flask import Flask, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from speech_to_text import record_and_transcribe  # 語音轉文字模組

app = Flask(__name__)
CORS(app)  # 允許跨域請求
socketio = SocketIO(app, cors_allowed_origins="*")  # 啟用 WebSocket

# 儲存逐字稿的模擬資料庫 (字典)
transcription_db = {}
chat_history = []  # 聊天歷史

@app.route("/")
def index():
    return "WebSocket Server is running!"

# 🎤 **1. 語音轉文字**
@socketio.on("speech_to_text")
def handle_speech(data):
    """處理 Base64 音訊並回傳逐字稿"""
    if "audio" not in data:
        emit("speech_error", {"error": "音訊檔案缺失"})
        return

    try:
        audio_data = base64.b64decode(data["audio"])
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(audio_data)
            temp_audio_path = temp_audio.name

        result = record_and_transcribe(temp_audio_path)
        os.remove(temp_audio_path)

        language = data.get("language", "zh")
        transcription = result.get(language, "")

        # 存入資料庫
        transcription_id = str(len(transcription_db) + 1)
        transcription_db[transcription_id] = {
            "zh": result["zh"],
            "en": result["en"],
            "de": result["de"],
            "ja": result["ja"]
        }

        emit("speech_result", {
            "transcription_id": transcription_id,
            "transcription": transcription,
        })

    except Exception as e:
        emit("speech_error", {"error": str(e)})

# 💾 **2. 儲存逐字稿**
@socketio.on("save_transcription")
def save_transcription(data):
    """儲存逐字稿內容"""
    transcription = data.get("transcription")
    language = data.get("language", "zh")

    if not transcription:
        emit("save_result", {"error": "逐字稿內容不可為空"})
        return

    transcription_id = str(len(transcription_db) + 1)
    transcription_db[transcription_id] = {language: transcription}

    emit("save_result", {"message": "逐字稿已儲存", "transcription_id": transcription_id})

# 📄 **3. 取得逐字稿**
@socketio.on("get_transcription")
def get_transcription(data):
    """根據 transcription_id 取得逐字稿"""
    transcription_id = data.get("transcription_id")
    language = data.get("language", "zh")

    if transcription_id not in transcription_db:
        emit("transcription_error", {"error": "找不到逐字稿"})
        return

    transcription = transcription_db[transcription_id].get(language, "")
    emit("transcription_result", {"transcription": transcription})

# 📜 **4. 取得逐字稿列表**
@socketio.on("get_all_transcriptions")
def get_all_transcriptions(data):
    """回傳所有逐字稿 ID"""
    keyword = data.get("keyword", "")
    timestamp = data.get("timestamp", "")

    transcriptions = [{"transcription_id": tid} for tid in transcription_db.keys()]
    emit("all_transcriptions_list", {"transcriptions": transcriptions})

# ❌ **5. 刪除逐字稿**
@socketio.on("delete_transcription")
def delete_transcription(data):
    """刪除逐字稿"""
    transcription_id = data.get("transcription_id")

    if transcription_id in transcription_db:
        del transcription_db[transcription_id]
        emit("delete_result", {"message": "逐字稿已刪除"})
    else:
        emit("delete_result", {"error": "找不到逐字稿"})

# 💬 **6. 發送聊天訊息**
@socketio.on("send_message")
def handle_chat(data):
    """發送聊天訊息"""
    message = data.get("message")

    if not message:
        emit("chat_response", {"error": "訊息不可為空"})
        return

    response = f"你說：{message} (目前回應為簡單回應)"
    chat_history.append({"user": message, "bot": response})

    emit("chat_response", {"message": response})

# 📚 **7. 取得聊天歷史**
@socketio.on("get_chat_history")
def get_chat_history():
    """取得聊天記錄"""
    emit("chat_history", {"history": chat_history})

if __name__ == "__main__":
    socketio.run(app, host="127.0.0.1", port=5000, debug=True)
