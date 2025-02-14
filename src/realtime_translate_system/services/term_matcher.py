import jieba
import MeCab
import pandas as pd
import re
from fuzzywuzzy import fuzz


class TermMatcher:
    def __init__(self, file_paths: dict, threshold: int = 90):
        """
        初始化 TermMatcher，支援多語言企業術語比對
        :param file_paths: 字典 { "語言名稱": "對應的 CSV 路徑" }
        :param threshold: 相似度閥值 (0-100)
        """
        self.threshold = threshold
        self.term_dicts = {}  # 存放不同語言的術語字典
        self.mecab = MeCab.Tagger("-Owakati")

        # 讀取每個語言的企業術語
        for lang, path in file_paths.items():
            self.term_dicts[lang] = self._load_glossaries(path)

        # 預設使用第一個語言（確保 `process_text()` 可單獨運行）
        self.default_lang = next(iter(file_paths))

        # 只對中文加入 jieba 詞庫，其他語言不需要
        if "Traditional Chinese" in self.term_dicts:
            self._add_terms_to_jieba(self.term_dicts["Traditional Chinese"])

    def _load_glossaries(self, file_path: str) -> dict:
        """讀取 CSV 並建立企業術語字典"""
        glossaries = pd.read_csv(file_path)
        glossaries.columns = glossaries.columns.str.strip()
        return {
            row["Proper Noun"]: row["Description"] for _, row in glossaries.iterrows()
        }

    def _add_terms_to_jieba(self, term_dict: dict) -> None:
        """將企業術語加入 jieba 詞庫，確保長詞優先匹配"""
        sorted_terms = sorted(term_dict.keys(), key=len, reverse=True)
        for term in sorted_terms:
            jieba.add_word(term)

    def _tokenize_text(self, input_text: str, lang: str) -> list:
        """根據語言選擇適當的分詞方式"""
        cleaned_text = re.sub(r"\s+", " ", input_text).strip()

        if lang == "Traditional Chinese":
            tokens = list(jieba.cut(cleaned_text))
        elif lang == "Japanese":
            tokens = self._tokenize_japanese(cleaned_text)
        else:
            # 英、德語：直接拆分單詞
            tokens = cleaned_text.split()

        return [token for token in tokens if token.strip()]

    def _tokenize_japanese(self, input_text: str) -> list:
        """使用 MeCab 進行日語分詞"""
        return self.mecab.parse(input_text).strip().split()

    def _fetch_terms(self, input_text: str, lang: str) -> list:
        """提取文本中被 `==` 包圍的詞彙"""
        terms = re.findall(r'==(.+?)==', input_text)
        return terms

    def _match_terms(self, tokens: list, term_dict: dict) -> tuple:
        """模糊比對詞彙，返回匹配的詞與相似度分數"""
        matched_terms = []
        similarity_scores = {}

        for token in tokens:
            best_match, best_score, best_desc = None, 0, ""
            for term in term_dict:
                score = fuzz.partial_ratio(token.lower(), term.lower())
                if score >= self.threshold and score > best_score:
                    best_match, best_score, best_desc = term, score, term_dict[term]

            if best_match:
                matched_terms.append((token, best_match, best_score, best_desc))
                similarity_scores[token] = best_score

        return matched_terms, similarity_scores

    def process_text(self, input_text: str, lang: str = None):
        """
        處理單語言文本。
        :param input_text: 需要處理的文本
        :param lang: 指定語言（若為 None，則使用預設語言）
        :return: (分詞後的 token 列表, 最終匹配的術語, 帶註釋的文本)
        """
        if lang is None:
            lang = self.default_lang
        if lang not in self.term_dicts:
            raise ValueError(f"Unsupported language: {lang}")

        term_dict = self.term_dicts[lang]
        terms = self._fetch_terms(input_text, lang)
        terms, similarity_scores = self._match_terms(terms, term_dict)
        explains = [desc for _, _, _, desc in terms]

        return explains, similarity_scores

    def process_multilingual_text(self, text_dict: dict):
        """
        處理多語言文本，依照不同語言使用對應的企業術語。

        :param text_dict: {"語言": "對應的文本"}
        :return: 相同結構的字典，但內容已加入企業術語註釋
        """
        output_dict = {}
        for lang, text in text_dict.items():
            if lang in self.term_dicts:
                explains, similarity_scores = self.process_text(text, lang)
                output_dict[lang] = {
                    "value": text,
                    "explains": explains,
                    "similarity_scores": similarity_scores,
                }
            else:
                output_dict[lang] = {
                    "value": text,
                    "explains": [],
                    "similarity_scores": {},
                }
        return output_dict


if __name__ == "__main__":
    from realtime_translate_system.config import Config

    matcher = TermMatcher(Config.FILE_PATHS)

    input_text = '''大家好，今天要討論的是關於DDR Ratio的問題，在 DP上發現這週的ratio很高，請問MARTIN是否知道發生原因 ?
很抱歉我昨天值大夜班，有把事情交接給LISA了，可以請他說明原因。
關於這周DDR ratio過高的原因可能是EC被動過的原因，我回去和母版比對後發現溫度等數值都不太一樣。
為什麼EC會被更改過，數值不是應該和母版對齊嗎? IT能不能查一下系統的log，確認做change的人是誰?
可以，我回去撈一下資料。
另外，IT能否也將做change的資料上架到DP，當有人做了不符合權限的事情可以印出資料，並自動寄送alert信件給相關人員。
好的，這件事技術上沒問題，但我需要回去和我老闆討論一下，因為這屬於架構上的change，我這邊需要新增cloud function來抓log的資料，BigQuery那邊也需要新增table欄位才行。
好，那請你下次再update這件事給我。另外EC被動過這件事也請Martin追一下發生原因，也請你下次update給我，謝謝。
好的，我這邊會持續追蹤這件事。
好了今天的會議就開到這邊，謝謝大家。
謝謝。
謝謝。
掰掰。''' 

    # merged_tokens, final_matched, annotated_text = matcher.process_text(
    #     input_text, "Traditional Chinese"
    # )
    # print("分詞結果：", merged_tokens)
    # print("\n最終偵測到的專有名詞：")
    # for token, term, score, description in final_matched:
    #     print(f"word: {token}, term: {term}, similarity: {score}%, desc: {description}")

    # print("\n帶註釋的文本：")
    # print(annotated_text)

    # 處理多語言文本
    text_to_annotate = {
        "Traditional Chinese": "大家好，今天要討論的是關於==DDR Ratio==的問題。",
        "English": "Hello, let's discuss the ==DDR Ratio== issue.",
        "German": "Hallo, wir sollten das ==DDR Ratio== Problem besprechen.",
        "Japanese": "こんにちは、==DDR Ratio==の問題について話し合いましょう。",
    }

    annotated_result = matcher.process_multilingual_text(text_to_annotate)

    for lang, text in annotated_result.items():
        print(f"=== {lang} ===")
        print(text)
        print()
