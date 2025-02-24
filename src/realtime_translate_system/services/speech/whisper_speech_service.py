import numpy as np
import queue
import torch
import webrtcvad
import whisper
from typing import Callable
import noisereduce as nr
from .speech2text_service import Speech2TextService

class WhisperSpeech2TextService(Speech2TextService):
    """Whisper Speech Recognizer class"""

    def __init__(self, model_size="large"):
        self.model = whisper.load_model(model_size)
        self.vad = webrtcvad.Vad()
        self.vad.set_mode(3)
        self.frame_rate = 16000
        self.sample_width = 2
        self.frame_duration = 30  # ms
        print(f"🔊 Whisper 模型已載入：{model_size}")

    def _is_speech(self, audio: bytes) -> bool:
        """Check if the audio contains speech"""
        return self.vad.is_speech(audio, self.frame_rate)

    def transcribe(self, audio_path: str, callback: Callable[[str], None]):
        """Transcribe a single audio file"""
        audio = whisper.load_audio(audio_path)
        # audio = whisper.pad_or_trim(audio)
        result = self.model.transcribe(audio, fp16=torch.cuda.is_available(), initial_prompt="""
        這是一段包含繁體中文、英語、日本語、德語的語音內容。請正確辨識所有語言並將其轉錄成文字，翻譯成中文。          
""")
        for r in result["segments"]:
            callback(r["text"])

    def transcribe_streaming(
        self,
        audio_queue: queue.Queue,
        callback: Callable[[str], None],
        done: Callable[[], None],
    ):
        """Simulate streaming transcription from an audio queue"""
        tmp_audio = b""
        chunk_size = 5  # Transcribe every 5 seconds of audio

        while True:
            exit_flag = False
            try:
                audio = audio_queue.get(timeout=3)
                if not audio:
                    break
                tmp_audio += audio
            except queue.Empty:
                exit_flag = True
                if not tmp_audio:
                    break

            frame_size = self.frame_rate * self.sample_width * self.frame_duration // 1000
            while len(tmp_audio) >= frame_size:
                frame = tmp_audio[:frame_size]
                tmp_audio = tmp_audio[frame_size:]
                if self._is_speech(frame):
                    break

            if len(tmp_audio) < chunk_size * self.frame_rate * self.sample_width:
                continue            

            audio = (
                np.frombuffer(tmp_audio, dtype=np.int16).astype(np.float32) / 32768.0
            )
            
            denoised_audio = nr.reduce_noise(y=audio, sr=self.frame_rate, prop_decrease=0.8)

            result = self.model.transcribe(denoised_audio, fp16=torch.cuda.is_available())
            text = result["text"].strip()
            callback(text)
            tmp_audio = b""
            if exit_flag:
                break
        done()  # Notify processing is done

if __name__ == "__main__":
    from pathlib import Path
    recognizer = WhisperSpeech2TextService()

    BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
    # audio_path = BASE_DIR / "dataset" / "training.wav"
    audio_path = BASE_DIR / "Testing.wav"

    print(audio_path)
    def callback(text):
        print(text)

    recognizer.transcribe(audio_path, callback)