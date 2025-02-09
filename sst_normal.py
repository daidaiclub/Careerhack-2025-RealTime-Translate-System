import os

from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech
from google.api_core.client_options import ClientOptions
from dotenv import load_dotenv
from pydub import AudioSegment
import webrtcvad
import math

import pandas as pd
import glob

glossaries = pd.read_csv("dataset/cmn-Hant-TW.csv", header=0)
proper_nouns = glossaries["Proper Noun "].tolist()
special_phrase = ["BigQuery"]
phrases = [
    {"value": phrase, "boost": 10 if phrase not in special_phrase else 20}
    for phrase in proper_nouns
]

load_dotenv()
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")


def from_dataset():
    audio_files = glob.glob("dataset/train_split_audio/*.wav")
    audio_files = sorted(audio_files, key=lambda x: int(x.split("/")[-1].split("_")[0]))
    return audio_files


import struct


def frame_generator(audio: AudioSegment, frame_duration_ms: int):
    """生成固定長度的 16-bit PCM 音訊片段"""
    frame_size = int(audio.frame_rate * frame_duration_ms / 1000) * audio.sample_width
    raw_audio = audio.raw_data
    for start in range(0, len(raw_audio), frame_size):
        frame = raw_audio[start : start + frame_size]
        if len(frame) == frame_size:  # 確保長度符合要求
            yield frame


def split_audio_vad(
    audio_path: str,
    frame_duration_ms: int = 30,
    vad_mode: int = 2,
    min_chunk_ms: int = 5000,
    silence_duration_ms: int = 60,
) -> list:
    """
    利用 VAD 切割音訊區段，並根據指定的 frame_duration_ms 與 silence_duration_ms
    動態計算需要連續多少個 frame 才算停留。

    參數：
      audio_path         - 音檔路徑
      frame_duration_ms  - 每個 frame 的長度（毫秒），例如 10、20、30ms
      vad_mode           - webrtcvad 模式 (0 ~ 3)
      min_chunk_ms       - 最小語音區段長度，低於此長度則不切割
      silence_duration_ms- 停留（靜音）的目標長度

    流程：
      1. 將音訊轉為單聲道 16kHz
      2. 根據 frame_duration_ms 切出 frame
      3. 每次遇到非語音 frame，累積 pending silence
         當累積數達到 required_silence_frames (計算方式：ceil(silence_duration_ms / frame_duration_ms))
         就判斷是否切割區段（如果當前區段達到 min_chunk_ms，就切割，不然則納入語音區段）
    """
    audio = AudioSegment.from_wav(audio_path)
    audio = audio.set_channels(1).set_frame_rate(16000)  # 確保為單聲道 16kHz

    vad = webrtcvad.Vad()
    vad.set_mode(vad_mode)

    frames = list(frame_generator(audio, frame_duration_ms))
    speech_chunks = []
    current_chunk = []
    pending_silence = 0
    pending_silence_frames = []
    min_chunk_frames = min_chunk_ms // frame_duration_ms
    # 動態計算需要連續多少個 frame 才算達到目標靜音長度
    required_silence_frames = math.ceil(silence_duration_ms / frame_duration_ms)

    for frame in frames:
        # 將 frame 轉換為 16-bit PCM (little-endian)
        frame_pcm = struct.unpack(f"{len(frame) // 2}h", frame)
        frame_bytes = struct.pack(f"{len(frame_pcm)}h", *frame_pcm)

        if vad.is_speech(frame_bytes, sample_rate=16000):
            # 如果之前累積的靜音不足目標長度，就納入 current_chunk
            if pending_silence_frames:
                current_chunk.extend(pending_silence_frames)
                pending_silence = 0
                pending_silence_frames = []
            current_chunk.append(frame_bytes)
        else:
            pending_silence += 1
            pending_silence_frames.append(frame_bytes)
            if pending_silence >= required_silence_frames:
                # 若 current_chunk 已達最小長度，就視為語音區段切割點
                if current_chunk and len(current_chunk) >= min_chunk_frames:
                    speech_chunks.append(b"".join(current_chunk))
                    current_chunk = []
                else:
                    # 否則，把這段靜音併入 current_chunk
                    current_chunk.extend(pending_silence_frames)
                pending_silence = 0
                pending_silence_frames = []

    if pending_silence_frames:
        current_chunk.extend(pending_silence_frames)
    if current_chunk:
        speech_chunks.append(b"".join(current_chunk))

    return [
        AudioSegment(data=chunk, sample_width=2, frame_rate=16000, channels=1)
        for chunk in speech_chunks
    ]


def split_audio(audio_path: str, chunk_ms: int = 800) -> list:
    """Splits an audio file into chunks.
    Args:
        audio_path (str): Path to the local audio file to be split.
            Example: "resources/audio.wav"
        chunk_ms (int): The duration of each chunk in milliseconds.
            Example: 800
    Returns:
        list: A list of AudioSegment objects representing the audio chunks.
    """

    audio = AudioSegment.from_wav(audio_path)
    audio = audio.set_channels(1).set_frame_rate(16000)

    chunks = [audio[i : i + chunk_ms] for i in range(0, len(audio), chunk_ms)]

    return chunks


def prepare_phrases(csv_path: str = "dataset/cmn-Hant-TW.csv") -> list:
    glossaries = pd.read_csv(csv_path, header=0)
    proper_nouns = glossaries["Proper Noun "].tolist()
    special_phrase = ["BigQuery"]
    phrases = [
        {"value": phrase, "boost": 10 if phrase not in special_phrase else 20}
        for phrase in proper_nouns
    ]

    return phrases


def transcribe_sync_chirp2(
    audio_file: str = None,
    audio: AudioSegment = None,
) -> cloud_speech.RecognizeResponse:
    """Transcribes an audio file using the Chirp 2 model of Google Cloud Speech-to-Text V2 API.
    Args:
        audio_file (str): Path to the local audio file to be transcribed.
            Example: "resources/audio.wav"
    Returns:
        cloud_speech.RecognizeResponse: The response from the Speech-to-Text API containing
        the transcription results.
    """

    # Instantiates a client
    phrases = prepare_phrases()
    client = SpeechClient(
        client_options=ClientOptions(
            api_endpoint="us-central1-speech.googleapis.com",
        )
    )

    # Reads a file as bytes
    if audio_file:
        with open(audio_file, "rb") as f:
            audio_content = f.read()
    else:
        audio_content = audio.export(format="wav").read()

    config = cloud_speech.RecognitionConfig(
        auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
        language_codes=["de-DE"],
        model="chirp_2",
        features=cloud_speech.RecognitionFeatures(enable_automatic_punctuation=True),
        adaptation=(
            cloud_speech.SpeechAdaptation(
                phrase_sets=[
                    cloud_speech.SpeechAdaptation.AdaptationPhraseSet(
                        inline_phrase_set=cloud_speech.PhraseSet(phrases=phrases)
                    )
                ]
            )
            if phrases
            else None
        ),
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


if __name__ == "__main__":
    from_dataset_type = True
    if from_dataset_type:
        audio_files = from_dataset()
        for audio in audio_files:
            transcribe_sync_chirp2(audio_file=audio)
    else:
        # audios = split_audio("dataset/training.wav", chunk_ms=6000)
        audio_files = from_dataset()
        audios = split_audio_vad(
            "dataset/training.wav", frame_duration_ms=10, vad_mode=1, min_chunk_ms=400, silence_duration_ms=460
        )
        print(f"Split {len(audios)} audio chunks")
        total = 0
        print("Start\tEnd\tAStart\tAEnd")
        for idx, audio in enumerate(audios):
            if idx >= len(audio_files):
                l, r = 'OOE', 'OOE'
            else:
                l, r = audio_files[idx].replace('.wav', '').split("/")[-1].split("_")[-2:]
            print(total, total + len(audio), l, r, sep='\t')
            total += len(audio)
            # transcribe_sync_chirp2(audio=audio)
        print(f"Total: {total}")
