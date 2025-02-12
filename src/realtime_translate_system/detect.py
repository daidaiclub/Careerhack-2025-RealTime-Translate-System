import os
import numpy as np
import speech_recognition as sr
import whisper
import torch

from datetime import datetime, timedelta
from queue import Queue
from time import sleep
from sys import platform

# 固定參數
MODEL_NAME = "base"  # Whisper 多語言模型
ENERGY_THRESHOLD = 1000  # 麥克風音量閾值，決定是否偵測到語音
RECORD_TIMEOUT = 2  # 每段錄音的長度（秒）
PHRASE_TIMEOUT = 1  # 句子結束的間隔（秒）

def Record():
    phrase_time = None
    data_queue = Queue()
    recorder = sr.Recognizer()
    recorder.energy_threshold = ENERGY_THRESHOLD
    recorder.dynamic_energy_threshold = False

    # 設置麥克風
    if 'linux' in platform:
        mic_name = "pulse"
        for index, name in enumerate(sr.Microphone.list_microphone_names()):
            if mic_name in name:
                source = sr.Microphone(sample_rate=16000, device_index=index)
                break
    else:
        source = sr.Microphone(sample_rate=16000)

    # 加載 Whisper 模型（支援多語言）
    audio_model = whisper.load_model(MODEL_NAME)

    transcription = ['']

    with source:
        recorder.adjust_for_ambient_noise(source)

    def record_callback(_, audio: sr.AudioData) -> None:
        """回調函數，將音頻數據存入隊列"""
        data_queue.put(audio.get_raw_data())

    # 開啟後台錄音
    recorder.listen_in_background(source, record_callback, phrase_time_limit=RECORD_TIMEOUT)
    print("🎙️ 語音輸入啟動，請開始說話（可混合多語言）...\n")

    while True:
        try:
            now = datetime.utcnow()
            if not data_queue.empty():
                phrase_complete = False
                if phrase_time and now - phrase_time > timedelta(seconds=PHRASE_TIMEOUT):
                    phrase_complete = True
                phrase_time = now

                # 組合音頻數據
                audio_data = b''.join(data_queue.queue)
                data_queue.queue.clear()

                # 轉換音頻格式
                audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

                # 轉錄音頻（不偵測語言）
                result = audio_model.transcribe(audio_np, fp16=torch.cuda.is_available())

                text = result['text'].strip()

                # 根據暫停情況更新轉錄文本
                if phrase_complete:
                    transcription.append(text)
                else:
                    transcription[-1] = text

                # 清屏並輸出轉錄結果
                os.system('cls' if os.name == 'nt' else 'clear')
                print("📝 轉錄內容：")
                for line in transcription:
                    print(line)

            else:
                sleep(0.25)
        except KeyboardInterrupt:
            break

    print("\n\n📜 最終轉錄結果：")
    for line in transcription:
        print(line)