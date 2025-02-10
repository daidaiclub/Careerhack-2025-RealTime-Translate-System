import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig, Part

import os
from dotenv import load_dotenv
load_dotenv()
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
vertexai.init(project=PROJECT_ID, location="us-central1")

model = GenerativeModel("gemini-1.5-pro-002")

prompt = """
Can you transcribe this interview, in the format of timecode, speaker, caption.
Use speaker A, speaker B, etc. to identify speakers.
Language: English, German, Hant-TW, Japanese.
"""

audio_file_uri = f"gs://{PROJECT_ID}-bucket/dataset/training.wav"
audio_file = Part.from_uri(audio_file_uri, mime_type="audio/mpeg")

contents = [audio_file, prompt]

response = model.generate_content(contents, generation_config=GenerationConfig(audio_timestamp=True))

print(response.text)