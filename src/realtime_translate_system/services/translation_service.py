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
            - You MUST strictly refer to the Term Dictionary to ensure the correct usage of terms during translation.
            - If a term from the Term Dictionary appears in the sentence, you **MUST use the exact translation provided in the dictionary**.
            - **If the original sentence contains an incorrect or non-standard form of a term, correct it to match the proper term in the dictionary before translating.**

            **Term Dictionary (STRICTLY FOLLOW THIS LIST):**
            {term_dict}
            
            **Example:**
            1. Input Sentence: "I worked night shift yesterday."
            Output:  "我昨天上大夜班。" 
            
            2. Input Sentence: "This device's AlnMark needs to be repositioned."
            Output:  "這台設備的 Alignment mark 需要重新調整位置。"


        3. **To ensure contextual consistency, here is the translation of the previous sentence for reference**
            {previous_translation_text}

        4. **Output Format**
            - Your response **must be enclosed within ```json and ```**.
            - **Do not include any explanations, only return the JSON object**.
            - The JSON format must strictly follow this structure:
        
        ```json
        {{
            {Language.TW}: "<translated Traditional Chinese text>",
            {Language.EN}: "<translated English text>",
            {Language.DE}: "<translated German text>",
            {Language.JP}: "<translated Japanese text>"
        }}
        ```
        
        ### Examples:
        1. Input Sentence: "這是一個測試。"  
        
        Output: 
        ```json
        {{
            {Language.TW}: "這是一個測試。",
            {Language.EN}: "This is a test.",
            {Language.DE}: "Das ist ein Test.",
            {Language.JP}: "これはテストです。"
        }}
        ```
        
        2. Input Sentence: "Gestern hatten wir ein wichtiges Meeting über KI-Technologien."  
        
        Output: 
        ```json
        {{
            {Language.TW}: "昨天我們有一場重要的關於人工智慧技術的會議。",
            {Language.EN}: "Yesterday we had an important meeting about AI technologies.",
            {Language.DE}: "Gestern hatten wir ein wichtiges Meeting über KI-Technologien.",
            {Language.JP}: "昨日、私たちはAI技術に関する重要な会議を行いました。"
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
        
        
        formatted_term_dict = "\n".join([
            f"- **{dfs[Language.EN].iloc[i]['Proper Noun ']}**:"
            f"\n  - zh: {dfs[Language.TW].iloc[i]['Proper Noun ']}, "
            f"en: {dfs[Language.EN].iloc[i]['Proper Noun ']}, "
            f"de: {dfs[Language.DE].iloc[i]['Proper Noun ']}, "
            f"jp: {dfs[Language.JP].iloc[i]['Proper Noun ']} / {katakana_dict.get(dfs[Language.EN].iloc[i]['Proper Noun '], dfs[Language.JP].iloc[i]['Proper Noun '])}"
            f"\n  - **Description**: {dfs[Language.EN].iloc[i]['Description']}"
            for i in range(len(dfs[Language.EN]))
        ])

        # formatted_term_dict = "\n".join(
        #     [
        #         f"- {dfs[Language.EN].iloc[i]['Proper Noun ']}: {dfs[Language.TW].iloc[i]['Proper Noun ']} (繁體中文), "
        #         f"{dfs[Language.EN].iloc[i]['Proper Noun ']} (英文), {dfs[Language.DE].iloc[i]['Proper Noun ']} (德文), "
        #         f"{dfs[Language.JP].iloc[i]['Proper Noun ']} / {katakana_dict.get(dfs[Language.JP].iloc[i]['Proper Noun '], dfs[Language.JP].iloc[i]['Proper Noun '])} (日文)"
        #         for i in range(len(dfs[Language.EN]))
        #     ]
        # )

        return formatted_term_dict


if __name__ == "__main__":
    transcripts = """
Hello everyone. Today we are going to discuss the issue regarding DDR ratio. It was found out that the ratio on DP is quite high this week. Does Martin know the reason?
Es tut mir leid, ich hatte gestern Nachtschicht und habe die Angelegenheiten an Lisa übergeben, er kann den Grund erklären.
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
