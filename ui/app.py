from flask import Flask, request
from flask_socketio import SocketIO, emit
from speech_to_text import record_and_transcribe
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 解決 CORS 問題
socketio = SocketIO(app, cors_allowed_origins="*")  # 啟用 WebSocket

@app.route("/")
def index():
    return "WebSocket Server is running!"

@socketio.on("start_speech")
def handle_speech(data):
    """ 接收前端請求，執行語音轉換並回傳結果 """

    # 執行語音轉換
    result = record_and_transcribe()

    # 回傳轉換結果
    emit("speech_result", {
        "zh": result[0],  # 中文
        "en": result[1],  # 英文
        "de": result[2],  # 德文
        "ja": result[3],  # 日文
        "definitions": result[4] if len(result) > 4 else {}
    })

if __name__ == "__main__":
    socketio.run(app, host="127.0.0.1", port=5000, debug=True)