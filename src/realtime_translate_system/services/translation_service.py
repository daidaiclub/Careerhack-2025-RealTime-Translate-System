import pandas as pd
import time
from vertexai.generative_models import GenerativeModel
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

    def translate(self, content: str, previous_translation: dict = None, term_dict: str = "") -> str:
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
                previous_sentence=previous_translation.get("previous_sentence", "None") if previous_translation else "None",
                zh=previous_translation.get("zh", "None") if previous_translation else "None",
                en=previous_translation.get("en", "None") if previous_translation else "None",
                de=previous_translation.get("de", "None") if previous_translation else "None",
                jp=previous_translation.get("jp", "None") if previous_translation else "None",
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
            "zh": "<translated Traditional Chinese text>",
            "en": "<translated English text>",
            "de": "<translated German text>",
            "jp": "<translated Japanese text>"
        }}
        ```
        
        ### Examples:
        1. Input Sentence: "這是一個測試。"  
        
        Output: 
        ```json
        {{
            "zh": "這是一個測試。",
            "en": "This is a test.",
            "de": "Das ist ein Test.",
            "jp": "これはテストです。"
        }}
        ```
        
        2. Input Sentence: "Gestern hatten wir ein wichtiges Meeting über KI-Technologien."  
        
        Output: 
        ```json
        {{
            "zh": "昨天我們有一場重要的關於人工智慧技術的會議。",
            "en": "Yesterday we had an important meeting about AI technologies.",
            "de": "Gestern hatten wir ein wichtiges Meeting über KI-Technologien.",
            "jp": "昨日、私たちはAI技術に関する重要な会議を行いました。"
        }}
        ```

        Now, translate the following sentence into the required languages and return only a valid JSON object enclosed within ```json and ```.

        **Input Sentence:**  
        {content}
        """

        response = self.llm_service.query(prompt, self.generation_config)
        parsed_response = self.llm_service.parse_json_response(response)

        return {
            "previous_sentence": content.strip(),
            "zh": parsed_response.get("zh", "None"),
            "en": parsed_response.get("en", "None"),
            "de": parsed_response.get("de", "None"),
            "jp": parsed_response.get("jp", "None")
        }

    def load_term_dict(self, glossaries_path="") -> str:
        """
        讀取並格式化專有名詞對應表
        """
        paths = {
            "zh": glossaries_path + "/cmn-Hant-TW.csv",
            "de": glossaries_path + "/de-DE.csv",
            "en": glossaries_path + "/en-US.csv",
            "jp": glossaries_path + "/ja-JP.csv"
        }

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
            "Vertex AI": "バーテックス エーアイ"
            }


        dfs = {lang: pd.read_csv(path) for lang, path in paths.items()}
        
        formatted_term_dict = "\n".join([
            f"- {dfs['en'].iloc[i]['Proper Noun ']}: {dfs['zh'].iloc[i]['Proper Noun ']} (繁體中文), "
            f"{dfs['en'].iloc[i]['Proper Noun ']} (英文), {dfs['de'].iloc[i]['Proper Noun ']} (德文), "
            f"{dfs['jp'].iloc[i]['Proper Noun ']} / {katakana_dict.get(dfs['jp'].iloc[i]['Proper Noun '], dfs['jp'].iloc[i]['Proper Noun '])} (日文)"
            for i in range(len(dfs['en']))
        ])
        
        return formatted_term_dict

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
