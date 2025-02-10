import base64
import vertexai
from vertexai.generative_models import GenerativeModel, Part, FinishReason
import vertexai.preview.generative_models as generative_models

MAX_OUTPUT_TOKENS = 1000
TEMPERATURE = 1.0
TOP_P = 0.95
TOP_K = 3

import os
from dotenv import load_dotenv

load_dotenv()
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
location = "us-central1"
vertexai.init(project=PROJECT_ID, location=location)


def translate(content: str = "Text to translate"):
    model = GenerativeModel("gemini-1.5-flash-002")
    responses = model.generate_content(
        [
            f"""SOURCE_LANGUAGE_CODE: auto
TARGET_LANGUAGE_CODE:cmn-Hant-TW""",
            content,
        ],
        generation_config=generation_config,
        #   safety_settings=safety_settings,
        stream=True,
    )

    for response in responses:
        print(response.text, end='')

    # print(responses.text)

generation_config = {
    "candidate_count": 1,
    "max_output_tokens": MAX_OUTPUT_TOKENS,
    "temperature": TEMPERATURE,
    "top_p": TOP_P,
    "top_k": TOP_K,
}

safety_settings = {
    generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
}

transcripts = """
Hello everyone, today we are going to discuss the issue regarding DDR Ratio. It was found that the ratio on DP is quite high this week. Does Martin know the reason?
Es tut mir leid, ich hatte gestern Nachtschicht und habe die Angelegenheiten an Lisa übergeben. Er kann den Grund erklären.
今週の DDR Ratio が高すぎる原因は、EC が変更された可能性があります。元のバージョンと比較したところ、温度などの数値がかなり違っていました。
Why was EC altered? Shouldn't the values align with the master copy? Can IT check the system log to identify who made the change?
可以，我回去撈一下資料。
Additionally, can IT upload the change data to DP? When someone does something unauthorized, it can print out the data and automatically send an alert email to the relevant personnel."
好的，這件事技術上沒問題，但我需要回去和我老闆討論一下，因為這屬於架構上的change，我這邊需要新增Cloud Function來抓log的資料，BigQuery那邊也需要新增table欄位才行。
Alright, please update me on this matter next time. Also, Martin, please investigate why EC was changed and update me next time. Thank you.
Alles klar, ich werde die Angelegenheit weiterverfolgen.
That concludes today's meeting, thank you everyone.
Danke.
ありがとうございます。
掰掰。
"""

import time

total_time = 0
for transcript in transcripts.split("\n"):
    if transcript:
        start = time.time()
        translate(transcript)
        total_time += time.time() - start
    
print(f"Total time: {total_time}, Average time: {total_time/len(transcripts.split("\n"))}")
