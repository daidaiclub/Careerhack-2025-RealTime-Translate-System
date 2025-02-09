import io
import time
import os
from google.api_core.client_options import ClientOptions
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech
from pydub import AudioSegment
from dotenv import load_dotenv

load_dotenv()
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
print(PROJECT_ID)

client = SpeechClient(
    client_options=ClientOptions(
        api_endpoint="us-central1-speech.googleapis.com",
    )
)

# 使用 manual_decoding_config 指定音訊格式與取樣率
streaming_config = cloud_speech.StreamingRecognitionConfig(
    config=cloud_speech.RecognitionConfig(
        language_codes=["cmn-Hant-TW"],
        model="chirp_2",
        features=cloud_speech.RecognitionFeatures(enable_automatic_punctuation=True),
        explicit_decoding_config=cloud_speech.ExplicitDecodingConfig(
            encoding=cloud_speech.ExplicitDecodingConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            audio_channel_count=1,
        ),
    ),
    streaming_features=cloud_speech.StreamingRecognitionFeatures(
        # interim_results=True,
    ),
)

# 讀取音檔，轉成單聲道 16kHz
# audio_path = "dataset/train_split_audio/1_Daisy_891_11877.wav"
audio_path = "dataset/training.wav"
audio = AudioSegment.from_wav(audio_path)
audio = audio.set_channels(1).set_frame_rate(16000)

# 每 750 毫秒為一個 chunk（約 24KB）
CHUNK_MS = 750
chunks = [audio[i : i + CHUNK_MS] for i in range(0, len(audio), CHUNK_MS)]

config_request = cloud_speech.StreamingRecognizeRequest(
    recognizer=f"projects/{PROJECT_ID}/locations/us-central1/recognizers/_",
    streaming_config=streaming_config,
)


def audio_generator():
    yield config_request
    for chunk in chunks:
        raw_audio = chunk.raw_data
        yield cloud_speech.StreamingRecognizeRequest(audio=raw_audio)
        # time.sleep(CHUNK_MS / 1000)


response = client.streaming_recognize(requests=audio_generator())

for result in response:
    for alt in result.results:
        print(f"👂 {alt.alternatives[0].transcript}", flush=True)
