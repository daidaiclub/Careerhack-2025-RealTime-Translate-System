import jieba
import pandas as pd
from fuzzywuzzy import fuzz
import re

# 讀取企業術語庫並提取 Proper Noun
def load_terms(file_path):
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip()  # 去除欄位名稱的多餘空格
    proper_nouns = set(df['Proper Noun'].dropna().tolist())  # 提取企業名詞
    
    # 將 Proper Noun 加入 Jieba 詞典，確保不被拆開
    for term in proper_nouns:
        jieba.add_word(term, freq=100000)
    
    return proper_nouns

# 進行分詞並刪除空格
def segment_text(text):
    return [word.strip() for word in jieba.lcut(text) if word.strip()]

# 計算分詞對企業詞彙的相似度
def compute_similarity_scores(words, proper_nouns):
    scores = []
    for word in words:
        best_match = max(proper_nouns, key=lambda term: fuzz.partial_ratio(word, term))
        score = fuzz.partial_ratio(word, best_match)
        scores.append((word, best_match, score))
    return scores

# 檢查是否為純英文詞
def is_english_word(word):
    return bool(re.match(r'^[A-Za-z\s]+$', word))

# 合併相鄰高相似度詞，並重新比對最佳企業詞彙
def merge_and_search_best_match(scores, proper_nouns, threshold=80):
    merged_terms = []
    i = 0
    while i < len(scores):
        if i < len(scores) - 1:
            word1, match1, score1 = scores[i]
            word2, match2, score2 = scores[i + 1]
            
            # 若相鄰詞分數都高於閾值，則合併並重新查找最佳企業詞彙
            if score1 >= threshold and score2 >= threshold:
                print(f"合併詞: {word1} + {word2}")
                if is_english_word(word1) or is_english_word(word2):
                    combined_word = word1 + " " + word2
                else:
                    combined_word = word1 + word2
                best_combined_match = max(proper_nouns, key=lambda term: fuzz.partial_ratio(combined_word, term))
                combined_score = fuzz.partial_ratio(combined_word, best_combined_match)
                
                # 若合併後的詞更符合某個專有名詞，則使用合併結果
                if combined_score >= threshold:
                    merged_terms.append((combined_word, best_combined_match, combined_score))
                    i += 2  # 跳過下一個詞
                    continue
        
        # 若無法合併，則單獨加入
        merged_terms.append(scores[i])
        i += 1
    
    return [(word, match, score) for word, match, score in merged_terms if score >= threshold]

# 從文本中提取企業名詞
def extract_proper_nouns(text, proper_nouns, threshold=80):
    words = segment_text(text)
    scores = compute_similarity_scores(words, proper_nouns)
    merged_terms = merge_and_search_best_match(scores, proper_nouns, threshold)
    return merged_terms

# 測試
def main():
    proper_nouns = load_terms("dataset/cmn-Hant-TW.csv")  # 讀取企業術語庫
    text = '''大家好，今天要討論的是關於DDR Ratio的問題，在 DP上發現這週的ratio很高，請問MARTIN是否知道發生原因 ?
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
    
    print("\n[分詞結果]")
    print(segment_text(text))  # 確認分詞結果
    
    detected_terms = extract_proper_nouns(text, proper_nouns)
    print("\n[偵測到的企業名詞]")
    for term in detected_terms:
        print(f"輸入詞: {term[0]}, 匹配詞: {term[1]}, 相似度: {term[2]}")

if __name__ == "__main__":
    main()