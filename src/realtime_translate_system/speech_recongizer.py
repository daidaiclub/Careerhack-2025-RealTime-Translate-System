import os
from google.api_core.client_options import ClientOptions
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech
from pydub import AudioSegment
from dotenv import load_dotenv
import pandas as pd
import queue
from typing import Generator, List, Callable

# 加載環境變數
load_dotenv()
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = "us-central1"


class SpeechRecognizer:
    _instance = None

    def __new__(cls):
        """確保 Singleton 模式"""
        if cls._instance is None:
            cls._instance = super(SpeechRecognizer, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """初始化 Google Speech Client"""
        self.client = SpeechClient(
            client_options=ClientOptions(
                api_endpoint=f"{LOCATION}-speech.googleapis.com"
            )
        )
        self.phrases = self._load_glossaries()
        self.streaming_config = self._create_streaming_config()

    def _load_glossaries(self) -> List[dict]:
        """載入術語表"""
        try:
            glossaries = pd.read_csv("../../dataset/cmn-Hant-TW.csv", header=0)
            proper_nouns = glossaries["Proper Noun "].dropna().tolist()
            special_phrase = ["BigQuery"]
            return [
                {"value": phrase, "boost": 10 if phrase not in special_phrase else 20}
                for phrase in proper_nouns
            ]
        except FileNotFoundError:
            print("⚠️ Glossary file not found. Skipping adaptation.")
            return []

    def _create_streaming_config(
        self, audio_decoding="wav_config"
    ) -> cloud_speech.StreamingRecognitionConfig:
        """建立 Google Speech Streaming 設定"""
        adaptation = (
            cloud_speech.SpeechAdaptation(
                phrase_sets=[
                    cloud_speech.SpeechAdaptation.AdaptationPhraseSet(
                        inline_phrase_set=cloud_speech.PhraseSet(phrases=self.phrases)
                    )
                ]
            )
            if self.phrases
            else None
        )

        audio_config = cloud_speech.ExplicitDecodingConfig(
            encoding=cloud_speech.ExplicitDecodingConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            audio_channel_count=1,
        )

        return cloud_speech.StreamingRecognitionConfig(
            config=cloud_speech.RecognitionConfig(
                language_codes=["cmn-Hant-TW"],
                # language_codes=["de-DE"],
                model="chirp_2",
                features=cloud_speech.RecognitionFeatures(
                    enable_automatic_punctuation=True
                ),
                explicit_decoding_config=audio_config,
                adaptation=adaptation,
            ),
        )

    def _prepare_audio_chunks(
        self, audio_path: str, chunk_ms: int = 96
    ) -> List[AudioSegment]:
        """讀取音檔並分割為小塊"""
        try:
            audio = AudioSegment.from_wav(audio_path)
            audio = audio.set_channels(1).set_frame_rate(16000)
            return [audio[i : i + chunk_ms] for i in range(0, len(audio), chunk_ms)]
        except Exception as e:
            print(f"❌ Error loading audio: {e}")
            return []

    def _audio_generator(
        self, audio_chunks: List[AudioSegment] = None, audio_queue: queue.Queue = None
    ) -> Generator:
        """建立音頻流發送請求"""
        config_request = cloud_speech.StreamingRecognizeRequest(
            recognizer=f"projects/{PROJECT_ID}/locations/{LOCATION}/recognizers/_",
            streaming_config=self.streaming_config,
        )
        yield config_request

        if audio_chunks:
            for chunk in audio_chunks:
                yield cloud_speech.StreamingRecognizeRequest(audio=chunk.raw_data)
        elif audio_queue:
            tmp_audio = b""
            while True:
                try:
                    audio = audio_queue.get(timeout=3)
                    if not audio:
                        break
                    tmp_audio += audio
                    yield cloud_speech.StreamingRecognizeRequest(audio=audio)
                except queue.Empty:
                    break

            audio = AudioSegment(
                data=tmp_audio,
                sample_width=2,  # 16-bit PCM
                frame_rate=16000,
                channels=1
            )
            audio.export("tmp.wav", format="wav", codec="pcm_s16le")


    def transcribe(self, audio_path: str, callback=Callable[[str], None]):
        """執行音頻轉錄"""
        audio_chunks = self._prepare_audio_chunks(audio_path)
        if not audio_chunks:
            return

        response = self.client.streaming_recognize(
            requests=self._audio_generator(audio_chunks=audio_chunks)
        )

        for result in response:
            for alt in result.results:
                text = alt.alternatives[0].transcript
                callback(text)

    def transcribe_streaming(
        self, audio_queue: queue.Queue, callback: Callable[[str], None], done: Callable[[], None]
    ):
        """處理麥克風錄音 Blob"""
        response = self.client.streaming_recognize(requests=self._audio_generator(audio_queue=audio_queue))

        for result in response:
            for alt in result.results:
                callback(alt.alternatives[0].transcript)

        done()


# **測試使用**
if __name__ == "__main__":
    recognizer = SpeechRecognizer()

    def callback(text):
        print(text)

    recognizer.transcribe("../../dataset/training.wav", callback)
