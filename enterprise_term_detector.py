import pandas as pd
import jieba
import re
from fuzzywuzzy import fuzz

# 讀取企業術語 CSV 檔案
file_path = "dataset/cmn-Hant-TW.csv"  # 修改成你的檔案路徑
glossaries = pd.read_csv(file_path)

# 清理欄位名稱
glossaries.columns = glossaries.columns.str.strip()

# 建立企業術語字典
term_dict = {row["Proper Noun"]: row["Description"] for _, row in glossaries.iterrows()}

# 排序企業術語，確保長詞優先匹配
sorted_terms = sorted(term_dict.keys(), key=len, reverse=True)

# 添加企業術語到 jieba 詞庫，確保正確分詞
for term in sorted_terms:
    jieba.add_word(term)

# 測試輸入文本
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

# **步驟 1：清理輸入文本（移除所有額外空格）**
input_text = re.sub(r'\s+', ' ', input_text).strip()  # 確保沒有多餘的空格

# **步驟 2：使用 jieba 進行分詞**
tokens = list(jieba.cut(input_text))

# **步驟 3：進一步移除分詞中的額外空格**
tokens = [t for t in tokens if t.strip()]  # 過濾掉單獨的空格

# **步驟 4：模糊比對，找出與企業術語相似的詞**
threshold = 60  # 設定相似度閥值
matched_terms = []  # 儲存匹配結果
similarity_scores = {}  # 記錄相似度分數

for word in tokens:
    best_match = None
    best_score = 0
    best_desc = ""

    for term in term_dict.keys():
        similarity = fuzz.ratio(word.lower(), term.lower())  # 計算相似度
        if similarity >= threshold and similarity > best_score:
            best_match = term
            best_score = similarity
            best_desc = term_dict[term]

    if best_match:
        matched_terms.append((word, best_match, best_score, best_desc))
        similarity_scores[word] = best_score  # 記錄相似度

# **步驟 5：合併相鄰高分詞**
merged_tokens = []
i = 0

while i < len(tokens):
    if i < len(tokens) - 1:
        word1 = tokens[i]
        word2 = tokens[i + 1]

        # 如果兩個詞都匹配了企業術語，且相似度都很高，則合併
        if word1 in similarity_scores and word2 in similarity_scores:
            if similarity_scores[word1] >= threshold and similarity_scores[word2] >= threshold:
                combined_word = word1 + " " + word2
                print(f"合併詞：{word1} + {word2} -> {combined_word}")
                merged_tokens.append(combined_word)
                i += 2  # 跳過下一個詞
                continue

    merged_tokens.append(tokens[i])
    i += 1

# **步驟 6：輸出分詞結果**
print("分詞結果：", merged_tokens)

# **步驟 7：從新的 merged_tokens 重新匹配企業術語**
final_matched_terms = []

for word in merged_tokens:
    best_match = None
    best_score = 0
    best_desc = ""

    for term in term_dict.keys():
        similarity = fuzz.ratio(word.lower(), term.lower())  # 計算相似度
        if similarity >= threshold and similarity > best_score:
            best_match = term
            best_score = similarity
            best_desc = term_dict[term]

    if best_match:
        final_matched_terms.append((word, best_match, best_score, best_desc))

# **步驟 8：輸出最終匹配的專有名詞**
print("\n最終偵測到的專有名詞：")
for word, term, score, description in final_matched_terms:
    print(f"word: {word}, term: {term}, similarity: {score}%")
