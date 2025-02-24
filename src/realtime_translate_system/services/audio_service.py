import os
from realtime_translate_system.extensions import socketio
from realtime_translate_system.config import Language
from .speech.speech2text_service import SpeechRecognizer
from .transcript_service import TranscriptService
from .meeting_service import MeetingProcessor
import noisereduce as nr
import numpy as np
import librosa
import soundfile as sf

class AudioService:
    def __init__(
        self,
        upload_folder,
        recognizer: SpeechRecognizer,
        transcript_service: TranscriptService,
        meeting_processor: MeetingProcessor,
    ):
        self.upload_folder = upload_folder
        self.recognizer: SpeechRecognizer = recognizer
        self.transcript_service: TranscriptService = transcript_service
        self.meeting_processor: MeetingProcessor = meeting_processor

        self.transcript_text = ""

    def process_audio(self, filename):
        filepath = os.path.join(self.upload_folder, filename)

        def callback(text):
            data = self.transcript_service.process(text)
            if data is not None:
                self.transcript_text += data["text"][Language.TW]["value"]
                socketio.emit("transcript", data, namespace="/audio_stream")

        self.recognizer.transcribe(filepath, callback)
        title, keywords = self.meeting_processor.gen_title_keywords(
            self.transcript_text
        )
        socketio.emit(
            "transcript",
            {"status": "complete", "title": title, "keywords": keywords},
            namespace="/audio_stream",
        )

    def noise_reduction_stream(self, audio: np.ndarray, sr: int, prop_decrease: float = 0.8) -> np.ndarray:
        """
        使用 noisereduce 進行語音降噪。

        :param audio: 輸入音訊 (np.ndarray, 1D)
        :param sr: 取樣率 (Hz)
        :param prop_decrease: 降噪強度 (0~1, 越高降噪越強)
        :return: 降噪後的音訊 (np.ndarray, 1D)
        """
        return nr.reduce_noise(y=audio, sr=sr, prop_decrease=prop_decrease)

    def noise_reduction_wav(self, input_wav: str, output_wav: str, prop_decrease: float = 0.8):
        """
        讀取 WAV 檔案並進行降噪處理。

        :param input_wav: 輸入的音檔路徑
        :param output_wav: 降噪後的輸出音檔路徑
        :param prop_decrease: 降噪強度 (0~1)
        """
        # 讀取音訊
        y, sr = librosa.load(input_wav, sr=None)

        # 降噪
        y_denoised = nr.reduce_noise(y=y, sr=sr, prop_decrease=prop_decrease)

        # 儲存降噪後的音檔
        sf.write(output_wav, y_denoised, sr)