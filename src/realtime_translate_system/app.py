from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import os
import queue
import threading
from werkzeug.utils import secure_filename
from realtime_translate_system.speech_recongizer import SpeechRecognizer
from realtime_translate_system.translate import TranslationService
from realtime_translate_system.term_matcher import TermMatcher

app = Flask(__name__)
CORS(app)  # 允許跨域請求
socketio = SocketIO(app, cors_allowed_origins="*")  # WebSocket 支援
recognizer = SpeechRecognizer()
translation_service = TranslationService()
audio_queue = queue.Queue()
thread_lock = threading.Lock()
file_paths = {
    "Traditional Chinese": "../dataset/cmn-Hant-TW.csv",
    "English": "../dataset/en-US.csv",
    "German": "../dataset/de-DE.csv",
    "Japanese": "../dataset/ja-JP.csv"
}
matcher = TermMatcher(file_paths)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"wav"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory("static", filename)


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "沒有上傳文件"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "沒有選擇文件"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        socketio.start_background_task(process_audio, filename)

        return jsonify({"message": "文件上傳成功", "filename": filename})

    return jsonify({"error": "不允許的文件類型"}), 400


def process_audio(filename):
    filename = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    def callback(text):
        text = translation_service.translate(text)
        text = matcher.process_multilingual_text(text)
        socketio.emit("transcript", text)

    recognizer.transcribe(filename, callback)
    socketio.emit("complete")


@socketio.on("audio_stream")
def handle_audio_stream(data):
    """
    處理 WebSocket 傳入的音頻流 (WebM Blob)，並即時轉錄
    """
    global start
    try:

        def callback(text):
            text = translation_service.translate(text)
            text = matcher.process_multilingual_text(text)
            socketio.emit("transcript_stream", text)

        def done():
            app.audio_task = None

        with thread_lock:
            if not hasattr(app, "audio_task") or app.audio_task is None:
                while True:
                    try:
                        audio_queue.get_nowait()
                    except queue.Empty:
                        break
                app.audio_task = socketio.start_background_task(
                    recognizer.transcribe_streaming, audio_queue, callback, done
                )
        audio_queue.put(data)
    except Exception as e:
        print(f"❌ Error processing audio stream: {e}")


if __name__ == "__main__":
    socketio.run(app, debug=True, host="0.0.0.0", port=5000)
