import os

from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech
from google.api_core.client_options import ClientOptions
from dotenv import load_dotenv
import pandas as pd

load_dotenv()
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")


def prepare_phrases(csv_path: str = "dataset/cmn-Hant-TW.csv") -> list:
    glossaries = pd.read_csv(csv_path, header=0)
    proper_nouns = glossaries["Proper Noun "].tolist()
    special_phrase = ["BigQuery"]
    phrases = [
        {"value": phrase, "boost": 10 if phrase not in special_phrase else 20}
        for phrase in proper_nouns
    ]

    return phrases


def transcribe_batch_chirp2(
    audio_uri: str,
) -> cloud_speech.BatchRecognizeResults:
    """Transcribes an audio file from a Google Cloud Storage URI using the Chirp 2 model of Google Cloud Speech-to-Text V2 API.
    Args:
        audio_uri (str): The Google Cloud Storage URI of the input audio file.
            E.g., gs://[BUCKET]/[FILE]
    Returns:
        cloud_speech.RecognizeResponse: The response from the Speech-to-Text API containing
        the transcription results.
    """
    use_chirp = True
    region = "us-central1" if use_chirp else "global"
    phrases = prepare_phrases()
    if not use_chirp:
        phrases = []

    # Instantiates a client
    client = SpeechClient(
        client_options=(
            ClientOptions(
                api_endpoint="us-central1-speech.googleapis.com",
            )
            if use_chirp
            else None
        )
    )

    config = cloud_speech.RecognitionConfig(
        features=cloud_speech.RecognitionFeatures(enable_automatic_punctuation=True),
        auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
        language_codes=["auto"],
        model="chirp_2" if use_chirp else "long",
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

    file_metadata = cloud_speech.BatchRecognizeFileMetadata(uri=audio_uri)

    request = cloud_speech.BatchRecognizeRequest(
        recognizer=f"projects/{PROJECT_ID}/locations/{region}/recognizers/_",
        config=config,
        files=[file_metadata],
        recognition_output_config=cloud_speech.RecognitionOutputConfig(
            inline_response_config=cloud_speech.InlineOutputConfig(),
        ),
        processing_strategy=cloud_speech.BatchRecognizeRequest.ProcessingStrategy.DYNAMIC_BATCHING,
    )

    # Transcribes the audio into text
    operation = client.batch_recognize(request=request)

    print("Waiting for operation to complete...")
    response = operation.result(timeout=120)

    for result in response.results[audio_uri].transcript.results:
        print(f"Transcript: {result.alternatives[0].transcript}")

    return response.results[audio_uri].transcript


if __name__ == "__main__":
    result = transcribe_batch_chirp2(f"gs://{PROJECT_ID}-bucket/dataset/training.wav")
    # print(result)
