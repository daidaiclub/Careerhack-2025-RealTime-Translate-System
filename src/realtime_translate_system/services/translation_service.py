import pandas as pd
import time
from vertexai.generative_models import GenerativeModel
from realtime_translate_system.config import Language
from realtime_translate_system.services.ai_service import LLMService


class TranslationService:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

        self.generation_config = {
            "candidate_count": 1,
            "max_output_tokens": 1000,
            "temperature": 0.2,
            "top_p": 0.8,
            "top_k": 5,
        }

    def translate(
        self, content: str, previous_translation: dict = None, term_dict: str = ""
    ) -> str:
        """
        進行翻譯並回傳結果
        """
        previous_translation_text = ""

        if previous_translation:
            previous_translation_text = """
            - Previous sentence: {previous_sentence}
            - The translation of the previous sentence is as follows:
            - Traditional Chinese: {zh}
            - English: {en}
            - German: {de}
            - Japanese: {jp}
            """.format(
                previous_sentence=(
                    previous_translation.get("previous_sentence", "None")
                    if previous_translation
                    else "None"
                ),
                zh=(
                    previous_translation.get(Language.TW, "None")
                    if previous_translation
                    else "None"
                ),
                en=(
                    previous_translation.get(Language.EN, "None")
                    if previous_translation
                    else "None"
                ),
                de=(
                    previous_translation.get(Language.DE, "None")
                    if previous_translation
                    else "None"
                ),
                jp=(
                    previous_translation.get(Language.JP, "None")
                    if previous_translation
                    else "None"
                ),
            )

        prompt = f"""
        You are a professional translator specializing in Traditional Chinese, English, German, and Japanese. Your task is to accurately translate the given sentence into these four languages while ensuring that the translation maintains **semantic meaning, grammar, and tone consistency**.

        ### Rules:
        1. **Input Language**
            - The input sentence will always be in one of the following languages: Traditional Chinese, English, German, or Japanese.
            - If the input language is not among these four, **return the original sentence without translation or modification**.

        2. **Handling of Term Dictionary (STRICTLY FOLLOW THE DICTIONARY)**    
            Step 1:
            - You MUST strictly refer to the Term Dictionary to ensure the correct usage of terms during translation.
            
            Step 2:
            - After completing the translation, **refer to the Term Dictionary**.
            - If a term from Term Dictionary appears in the translation, **enclose it with `==`**.
            - **Ensure that terms are correctly translated before marking them.** If a term has a specific translation in a target language, use the correct translation before marking it.
            - **ONLY** mark words that appear in Term Dictionary with `==`. Do **NOT** assume any other words are in Term Dictionary.
            
            **Term Dictionary (STRICTLY FOLLOW THIS LIST):**
            {term_dict}
            
            **Example:**
            - **Original Sentence:** "I worked night shift yesterday."
            - **Step 1 :** "我昨天上大夜班。"  
            - **Step 2 :** "我昨天上==大夜班==。"


        3. **To ensure contextual consistency, here is the translation of the previous sentence for reference**
            {previous_translation_text}

        4. **Output Format**
            - Your response **must be enclosed within ```json and ```**.
            - **Do not include any explanations, only return the JSON object**.
            - The JSON format must strictly follow this structure:
        
        ```json
        {{
            Language.TW: "<translated Traditional Chinese text>",
            Language.EN: "<translated English text>",
            Language.DE: "<translated German text>",
            Language.JP: "<translated Japanese text>"
        }}
        ```
        
        ### Examples:
        1. Input Sentence: "這是一個測試。"  
        
        Output: 
        ```json
        {{
            Language.TW: "這是一個測試。",
            Language.EN: "This is a test.",
            Language.DE: "Das ist ein Test.",
            Language.JP: "これはテストです。"
        }}
        ```
        
        2. Input Sentence: "Gestern hatten wir ein wichtiges Meeting über KI-Technologien."  
        
        Output: 
        ```json
        {{
            Language.TW: "昨天我們有一場重要的關於人工智慧技術的會議。",
            Language.EN: "Yesterday we had an important meeting about AI technologies.",
            Language.DE: "Gestern hatten wir ein wichtiges Meeting über KI-Technologien.",
            Language.JP: "昨日、私たちはAI技術に関する重要な会議を行いました。"
        }}
        ```

        Now, translate the following sentence into the required languages and return only a valid JSON object enclosed within ```json and ```.

        **Input Sentence:**  
        {content}
        """

        response = self.llm_service.query([prompt], self.generation_config)
        parsed_response = self.llm_service.parse_json_response(response)

        return {
            "previous_sentence": content.strip(),
            Language.TW: parsed_response.get(Language.TW, "None"),
            Language.EN: parsed_response.get(Language.EN, "None"),
            Language.DE: parsed_response.get(Language.DE, "None"),
            Language.JP: parsed_response.get(Language.JP, "None"),
        }

    def load_term_dict(self, glossaries_path="", glossaries_paths=[]) -> str:
        """
        讀取並格式化專有名詞對應表
        """
        paths = (
            {
                Language.TW: glossaries_path + "/cmn-Hant-TW.csv",
                Language.DE: glossaries_path + "/de-DE.csv",
                Language.EN: glossaries_path + "/en-US.csv",
                Language.JP: glossaries_path + "/ja-JP.csv",
            }
            if glossaries_path
            else glossaries_paths
        )

        # fix_maps = {
        #     "Traditional Chinese": Language.TW,
        #     "German": Language.DE,
        #     "English": Language.EN,
        #     "Japanese": Language.JP,
        # }

        # paths = {fix_maps[key]: str(value) for key, value in paths.items()}

        katakana_dict = {
            "DDR Ratio": "ディーディーアール レシオ",
            "EC": "イルシ",
            "ECS": "イルシエス",
            "ECCP": "イルシシーピー",
            "ECN": "イルシエヌ",
            "Emergency stop": "エマージェンシー ストップ",
            "Alignment mark": "アライメント マーク",
            "ALP": "エーエルピー",
            "STB": "エスティービー",
            "STK": "エスティーケー",
            "Route": "ルート",
            "Scrap": "スクラップ",
            "Sorter": "ソーター",
            "Split": "スプリット",
            "夜勤": "ヤキン",
            "準夜勤": "ジュンヤキン",
            "日勤": "ニッキン",
            "マスク": "マスク",
            "DP": "ディーピー",
            "SGP": "エスジーピー",
            "ETP": "イーティーピー",
            "Cloud Run": "クラウド ラン",
            "Cloud Function": "クラウド ファンクション",
            "BigQuery": "ビッグクエリ",
            "Pub/Sub": "パブサブ",
            "Cloud SQL": "クラウド エスキューエル",
            "Artifact Registry": "アーティファクト レジストリ",
            "Cloud Storage": "クラウド ストレージ",
            "GKE": "ジーケーイー",
            "Vertex AI": "バーテックス エーアイ",
        }

        dfs = {lang: pd.read_csv(path) for lang, path in paths.items()}

        formatted_term_dict = "\n".join(
            [
                f"- {dfs[Language.EN].iloc[i]['Proper Noun ']}: {dfs[Language.TW].iloc[i]['Proper Noun ']} (繁體中文), "
                f"{dfs[Language.EN].iloc[i]['Proper Noun ']} (英文), {dfs[Language.DE].iloc[i]['Proper Noun ']} (德文), "
                f"{dfs[Language.JP].iloc[i]['Proper Noun ']} / {katakana_dict.get(dfs[Language.JP].iloc[i]['Proper Noun '], dfs[Language.JP].iloc[i]['Proper Noun '])} (日文)"
                for i in range(len(dfs[Language.EN]))
            ]
        )

        return formatted_term_dict


if __name__ == "__main__":
    transcripts = """
Hello everyone. Today we are going to discuss the issue regarding DDR ratio. It was found out that the ratio on DP is quite high this week. Does Martin know the reason?
Es tut mir leid, ich hatte gestern Nachtschicht und habe die Angelegenheiten an Lisa übergeben, er kann den Grund erklären.
今週 の DDR 値 が 高 すぎる 原因 は イルシ が 変更 さ れ た 可能 性 が あり ます 。 マスター パージ と 比較 し た ところ 溫度 など の 周知 が かなり 違っ て い まし た 。
Why was EC altered? Shouldn't the values align with the master copy? Can I check the system log to identify who made the change?
可以,我現在要出去啦。
Additionally, can IT upload the change data to DP? When someone does something unauthorized, it can print out the data and automatically send an alert email to the relevant personnel.
好的,這件事技術上沒問題,但我需要回去和我老闆討論一下,因為這屬於架構上的change,我這邊需要新增Cloud Function來抓log的資料,BQuery那邊也需要新增table兩位才行。
Alright, please update me on this matter next time. Also, Martin, please investigate why easy was changed and update me next time. Thank you.
Alles klar, ich werde die Angelegenheit weiterverfolgen.
That concludes today's meeting. Thank you everyone.
登
ありがとう ござい ます 。
Bye-bye.
"""

    text_list = transcripts.split("\n")

    llm_service = LLMService("gemini-1.5-flash-002")
    service = TranslationService(llm_service)
    total_time = 0

    import pathlib

    term_dict_path = pathlib.Path(__file__).parent.parent / "glossaries"
    term_dict = service.load_term_dict(str(term_dict_path))

    import json

    previous_translation = None
    for text in text_list:
        if not text.strip():
            continue
        start_time = time.time()
        result = service.translate(
            text.strip(), previous_translation, term_dict=term_dict
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        total_time += time.time() - start_time

        previous_translation = result

    print(f"Total time: {total_time}, Average time: {total_time/len(text_list)}")
