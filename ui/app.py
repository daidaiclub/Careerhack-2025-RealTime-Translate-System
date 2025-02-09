from flask import Flask, request, jsonify
from speech_to_text import record_and_transcribe  # 你的 Python 語音函數
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 解決 CORS 問題，讓前端能請求後端

@app.route("/run_speech_to_text", methods=["POST"])
def process_speech():
    """ 接收前端請求，執行語音轉換 """
    data = request.json
    mode = data.get("mode", "標準模式")  # 讀取模式
    print(f"🎤 接收到語音請求，模式：{mode}")

    # 執行語音轉換（你的原本函數）
    result = record_and_transcribe(mode)

    return jsonify({
        "zh": result[0],  # 中文
        "en": result[1],  # 英文
        "de": result[2],  # 德文
        "ja": result[3],   # 日文
        "definitions": result[4] if len(result) > 4 else {}
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)