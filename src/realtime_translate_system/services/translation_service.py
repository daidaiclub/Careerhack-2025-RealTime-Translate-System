import re
import time
import vertexai
from vertexai.generative_models import GenerativeModel
import vertexai.preview.generative_models as generative_models


class TranslationService:
    def __init__(self, location: str = "us-central1", project_id: str = None):
        self.location = location
        self.project_id = project_id

        if not self.project_id:
            raise ValueError("Project ID is required for Vertex AI")

        vertexai.init(project=self.project_id, location=self.location)

        self.generation_config = {
            "candidate_count": 1,
            "max_output_tokens": 1000,
            "temperature": 1.0,
            "top_p": 0.95,
            "top_k": 3,
        }

        self.safety_settings = {
            generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }

        # 指定要用的模型
        self.model = GenerativeModel("gemini-1.5-flash-002")

    def _clean_translation_output(self, response: str):
        """
        解析並整理 Gemini Chat 的翻譯輸出，確保格式一致。
        """
        translations = {
            "Traditional Chinese": "",
            "English": "",
            "German": "",
            "Japanese": "",
        }

        # 解析每一行的語言與對應翻譯
        lines = response.strip().split("\n")
        correct_lang_count = 0
        for line in lines:
            match = re.match(
                r"- (Traditional Chinese|English|German|Japanese):\s*(.+)", line
            )
            if match:
                lang = match.group(1)
                text = match.group(2).strip()
                cleaned_text = re.sub(r"\(.*?\)", "", text).strip()
                translations[lang] = cleaned_text
                correct_lang_count += 1

        result = {
            "status": "success" if correct_lang_count == 4 else "error",
            "values": translations,
        }

        return result

    def translate(self, content: str) -> str:
        """
        進行翻譯並回傳結果
        """

        # TODO: 可以增加前面的逐字稿，提供給他上下文，讓翻譯更準確
        prompt = """
    You are a professional translator specializing in Traditional Chinese, English, German, and Japanese. Your task is to translate the given sentence into all four languages.

    Follow these rules:
    1. The input sentence will be in one of the following languages: Traditional Chinese, English, German, or Japanese.
    2. You must translate the sentence into:
       - Traditional Chinese
       - English
       - German
       - Japanese
    3. If the input language is not one of these four, return: "CAN NOT TRANSLATE."
    4. Ensure that the translations are natural, fluent, and maintain the original meaning.
    5. Proper nouns including names of people, places, and companies should not be translated.

    Provide the response in the following format:
    - Traditional Chinese: <translated text>
    - English: <translated text>
    - German: <translated text>
    - Japanese: <translated text>

    Input:
    """

        responses = self.model.generate_content(
            [prompt, content],
            generation_config=self.generation_config,
            safety_settings=self.safety_settings,
        )

        # 將逐行流式輸出合併成完整翻譯文字
        translated_text = self._clean_translation_output(responses.text)
        if translated_text["status"] == "error":
            translated_text = {
                "status": "error",
                "values": {
                    "Traditional Chinese": content,
                    "English": content,
                    "German": content,
                    "Japanese": content,
                },
            }

        return translated_text.get("values", {})


if __name__ == "__main__":
    transcripts = """
: Hello everyone. Today we are going to discuss the issue regarding DDR ratio. It was found out that the ratio on DP is quite high this week. Does Martin know the reason?
: Es tut mir leid, ich hatte gestern Nachtschicht und habe die Angelegenheiten an Lisa übergeben, er kann den Grund erklären.
: 今週 の DDR 値 が 高 すぎる 原因 は イルシ が 変更 さ れ た 可能 性 が あり ます 。 マスター パージ と 比較 し た ところ 溫度 など の 周知 が かなり 違っ て い まし た 。
: Why was EC altered? Shouldn't the values align with the master copy? Can I check the system log to identify who made the change?
: 可以,我現在要出去啦。
: Additionally, can IT upload the change data to DP? When someone does something unauthorized, it can print out the data and automatically send an alert email to the relevant personnel.
: 好的,這件事技術上沒問題,但我需要回去和我老闆討論一下,因為這屬於架構上的change,我這邊需要新增Cloud Function來抓log的資料,BQuery那邊也需要新增table兩位才行。
: Alright, please update me on this matter next time. Also, Martin, please investigate why easy was changed and update me next time. Thank you.
: Alles klar, ich werde die Angelegenheit weiterverfolgen.
: That concludes today's meeting. Thank you everyone.
: 登
: ありがとう ござい ます 。
: Bye-bye.
"""

    transcripts = """
: soigys ie yn ty
: owue hhhg kk
: This is a test.
: 這是一個測試。
: これはテストです。
: Das ist ein Test.
"""

    text_list = transcripts.split("\n")

    from realtime_translate_system.config import Config

    service = TranslationService(location=Config.LOCATION, project_id=Config.PROJECT_ID)
    total_time = 0
    import json

    for text in text_list:
        if not text.strip():
            continue
        start_time = time.time()
        result = service.translate(text.strip())
        print(json.dumps(result, indent=2, ensure_ascii=False))
        total_time += time.time() - start_time

    print(f"Total time: {total_time}, Average time: {total_time/len(text_list)}")
