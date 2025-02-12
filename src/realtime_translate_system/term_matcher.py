import pandas as pd
import jieba
import MeCab
import re
from fuzzywuzzy import fuzz

class TermMatcher:
    def __init__(self, file_paths: dict, threshold: int = 60):
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
        return {row["Proper Noun"]: row["Description"] for _, row in glossaries.iterrows()}

    def _add_terms_to_jieba(self, term_dict: dict) -> None:
        """將企業術語加入 jieba 詞庫，確保長詞優先匹配"""
        sorted_terms = sorted(term_dict.keys(), key=len, reverse=True)
        for term in sorted_terms:
            jieba.add_word(term)

    def _tokenize_text(self, input_text: str, lang: str) -> list:
        """根據語言選擇適當的分詞方式"""
        cleaned_text = re.sub(r'\s+', ' ', input_text).strip()

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

    def _match_terms(self, tokens: list, term_dict: dict) -> tuple:
        """模糊比對詞彙，返回匹配的詞與相似度分數"""
        matched_terms = []
        similarity_scores = {}

        for token in tokens:
            best_match, best_score, best_desc = None, 0, ""
            for term in term_dict:
                score = fuzz.ratio(token.lower(), term.lower())
                if score >= self.threshold and score > best_score:
                    best_match, best_score, best_desc = term, score, term_dict[term]

            if best_match:
                matched_terms.append((token, best_match, best_score, best_desc))
                similarity_scores[token] = best_score

        return matched_terms, similarity_scores

    def _merge_adjacent_tokens(self, tokens: list, similarity_scores: dict) -> list:
        """合併相鄰高相似度詞彙"""
        merged_tokens = []
        i = 0
        while i < len(tokens):
            if i < len(tokens) - 1:
                token1, token2 = tokens[i], tokens[i + 1]
                if token1 in similarity_scores and token2 in similarity_scores:
                    if similarity_scores[token1] >= self.threshold and similarity_scores[token2] >= self.threshold:
                        merged_tokens.append(token1 + " " + token2)
                        i += 2
                        continue
            merged_tokens.append(tokens[i])
            i += 1
        return merged_tokens

    def _final_matching(self, tokens: list, term_dict: dict) -> list:
        """重新比對合併後的詞彙，返回最終匹配結果"""
        final_matched = []

        for token in tokens:
            best_match, best_score, best_desc = None, 0, ""
            for term in term_dict:
                score = fuzz.ratio(token.lower(), term.lower())
                if score >= self.threshold and score > best_score:
                    best_match, best_score, best_desc = term, score, term_dict[term]

            if best_match:
                final_matched.append((token, best_match, best_score, best_desc))

        return final_matched

    def annotate_text(self, input_text: str, final_matched: list) -> str:
        """
        將匹配到的專有名詞替換為 原詞[定義] 的格式，避免重複替換已標記的內容。
        僅在不在中括號(...)的區域裡才會做替換，防止重複或嵌套注釋。
        """
        final_matched_sorted = sorted(final_matched, key=lambda x: len(x[0]), reverse=True)

        token_map = {}
        for token, term, score, desc in final_matched_sorted:
            if token.lower() not in token_map:
                token_map[token.lower()] = desc

        annotated_text = []
        inside_brackets = False  # 用來標記目前是否在 [ ] 中
        i = 0
        n = len(input_text)

        while i < n:
            ch = input_text[i]

            if ch == '[':
                # 一旦遇到 '['，表示進入中括號，直接將字元加入結果
                inside_brackets = True
                annotated_text.append(ch)
                i += 1
            elif ch == ']':
                # 一旦遇到 ']'，表示離開中括號，直接將字元加入結果
                inside_brackets = False
                annotated_text.append(ch)
                i += 1
            else:
                if not inside_brackets:
                    matched = False
                    for tk, desc in token_map.items():
                        token_len = len(tk)
                        if i + token_len <= n and input_text[i:i+token_len].lower() == tk:
                            original_str = input_text[i:i+token_len]
                            annotated_text.append(f"{original_str}[{desc}]")
                            i += token_len
                            matched = True
                            break
                    if not matched:
                        annotated_text.append(ch)
                        i += 1
                else:
                    annotated_text.append(ch)
                    i += 1

        return "".join(annotated_text)

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
        tokens = self._tokenize_text(input_text, lang)
        matched_terms, similarity_scores = self._match_terms(tokens, term_dict)
        merged_tokens = self._merge_adjacent_tokens(tokens, similarity_scores)
        final_matched = self._final_matching(merged_tokens, term_dict)
        annotated_text = self.annotate_text(input_text, final_matched)

        return merged_tokens, final_matched, annotated_text
    
    def process_multilingual_text(self, text_dict: dict):
        """
        處理多語言文本，依照不同語言使用對應的企業術語。
        
        :param text_dict: {"語言": "對應的文本"}
        :return: 相同結構的字典，但內容已加入企業術語註釋
        """
        output_dict = {}
        for lang, text in text_dict.items():
            if lang in self.term_dicts:
                output_dict[lang] = self.process_text(text, lang)[2]
            else:
                output_dict[lang] = text  # 未知語言則不做處理
        return output_dict

if __name__ == "__main__":
    file_paths = {
        "Traditional Chinese": "../../dataset/cmn-Hant-TW.csv",
        "English": "../../dataset/en-US.csv",
        "German": "../../dataset/de-DE.csv",
        "Japanese": "../../dataset/ja-JP.csv"
    }
    matcher = TermMatcher(file_paths)

    input_text = """
    大家好，今天要討論的是關於DDR Ratio的問題，在 DP上發現這週的ratio很高，請問MARTIN是否知道發生原因 ?
    """

    merged_tokens, final_matched, annotated_text = matcher.process_text(input_text, "Traditional Chinese")
    print("分詞結果：", merged_tokens)
    print("\n最終偵測到的專有名詞：")
    for token, term, score, description in final_matched:
        print(f"word: {token}, term: {term}, similarity: {score}%, desc: {description}")

    print("\n帶註釋的文本：")
    print(annotated_text)

    # 處理多語言文本
    text_to_annotate = {
        "Traditional Chinese": "大家好，今天要討論的是關於DDR Ratio的問題。",
        "English": "Hello, let's discuss the DDR Ratio issue.",
        "German": "Hallo, wir sollten das DDR Ratio Problem besprechen.",
        "Japanese": "こんにちは、DDR Ratioの問題について話し合いましょう。"
    }

    annotated_result = matcher.process_multilingual_text(text_to_annotate)

    for lang, text in annotated_result.items():
        print(f"=== {lang} ===")
        print(text)
        print()