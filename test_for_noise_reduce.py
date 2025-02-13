from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import whisper
from dotenv import load_dotenv
import vertexai
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech
from google.api_core.client_options import ClientOptions


app = Flask(__name__)
CORS(app)  # 允許跨域請求（CORS 問題）

load_dotenv()
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = "us-central1"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # 確保資料夾存在

def quickstart_v2(audio_file: str) -> cloud_speech.RecognizeResponse:
    """Transcribe an audio file.
    Args:
        audio_file (str): Path to the local audio file to be transcribed.
    Returns:
        cloud_speech.RecognizeResponse: The response from the recognize request, containing
        the transcription results
    """
    # Reads a file as bytes
    with open(audio_file, "rb") as f:
        audio_content = f.read()

    client = SpeechClient(
        client_options=ClientOptions(api_endpoint=f"{LOCATION}-speech.googleapis.com")
    )

    config = cloud_speech.RecognitionConfig(
        auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
        language_codes=["cmn-Hant-TW"],
        model="chirp_2",
    )

    request = cloud_speech.RecognizeRequest(
        recognizer=f"projects/{PROJECT_ID}/locations/us-central1/recognizers/_",
        config=config,
        content=audio_content,
    )

    # Transcribes the audio into text
    response = client.recognize(request=request)

    for result in response.results:
        print(f"Transcript: {result.alternatives[0].transcript}")

    return response


# # 載入 Whisper 模型（選擇 'base' 或 'small' 以加快速度）
# model = whisper.load_model("large")  # 你可以改成 'small', 'medium', 'large' 視需求而定

# @app.route("/upload_whisper", methods=["POST"])
# def upload_audio():
#     if "audio" not in request.files:
#         return jsonify({"error": "沒有接收到音訊檔案"}), 400

#     audio_file = request.files["audio"]
#     file_path = os.path.join(UPLOAD_FOLDER, audio_file.filename)
#     audio_file.save(file_path)
#     print(f"音訊已上傳至 {file_path}")
#     try:
#         # **Whisper 轉錄音檔**
#         result = model.transcribe(file_path)
#         text = result["text"]
        
#         return jsonify({"message": "音訊已轉錄", "transcription": text}), 200

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
    
@app.route("/upload_google", methods=["POST"])
def upload_audio_google():
    if "audio" not in request.files:
        return jsonify({"error": "沒有接收到音訊檔案"}), 400

    audio_file = request.files["audio"]
    file_path = os.path.join(UPLOAD_FOLDER, audio_file.filename)
    audio_file.save(file_path)
    print(f"音訊已上傳至 {file_path}")
    try:
        # **Google Cloud 轉錄音檔**
        response = quickstart_v2(file_path)
        text = response.results[0].alternatives[0].transcript

        return jsonify({"message": "音訊已轉錄", "transcription": text}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
