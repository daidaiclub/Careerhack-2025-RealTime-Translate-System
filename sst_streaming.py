import os
from google.api_core.client_options import ClientOptions
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech
from pydub import AudioSegment
from dotenv import load_dotenv

import pandas as pd

glossaries = pd.read_csv("dataset/cmn-Hant-TW.csv", header=0)
proper_nouns = glossaries["Proper Noun "].tolist()
special_phrase = ["BigQuery"]
phrases = [{"value": phrase, "boost": 10 if phrase not in special_phrase else 20} for phrase in proper_nouns]

load_dotenv()
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")

client = SpeechClient(
    client_options=ClientOptions(
        api_endpoint="us-central1-speech.googleapis.com",
    )
)

location = "us-central1"

# 使用 manual_decoding_config 指定音訊格式與取樣率
streaming_config = cloud_speech.StreamingRecognitionConfig(
    config=cloud_speech.RecognitionConfig(
        language_codes=["de-DE"],
        model="chirp_2",
        features=cloud_speech.RecognitionFeatures(enable_automatic_punctuation=True),
        explicit_decoding_config=cloud_speech.ExplicitDecodingConfig(
            encoding=cloud_speech.ExplicitDecodingConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            audio_channel_count=1,
        ),
        adaptation=cloud_speech.SpeechAdaptation(
            phrase_sets=[
                cloud_speech.SpeechAdaptation.AdaptationPhraseSet(
                    inline_phrase_set=cloud_speech.PhraseSet(phrases=phrases)
                )
            ]
        ) if phrases else None,
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

CHUNK_MS = 800
chunks = [audio[i : i + CHUNK_MS] for i in range(0, len(audio), CHUNK_MS)]

config_request = cloud_speech.StreamingRecognizeRequest(
    recognizer=f"projects/{PROJECT_ID}/locations/{location}/recognizers/_",
    streaming_config=streaming_config,
)


def audio_generator():
    yield config_request
    for chunk in chunks:
        raw_audio = chunk.raw_data
        yield cloud_speech.StreamingRecognizeRequest(audio=raw_audio)


response = client.streaming_recognize(requests=audio_generator())

for result in response:
    for alt in result.results:
        print(f"👂 {alt.alternatives[0].transcript}", flush=True)
