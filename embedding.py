import psycopg2
import numpy as np
import os
from dotenv import load_dotenv
from vertexai.language_models import TextEmbeddingModel
import vertexai
import ast 

# 載入環境變數
load_dotenv()
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = "us-central1"
MODEL_NAME = "text-embedding-005"

# 初始化 Vertex AI
vertexai.init(project=PROJECT_ID, location=LOCATION)

# 加載嵌入模型
embedding_model = TextEmbeddingModel.from_pretrained(MODEL_NAME)

# PostgreSQL 連線設定
DB_CONFIG = {
    "dbname": "meetings_db",
    "user": "postgres",
    "password": "postgres",
    "host": "127.0.0.1",  # Cloud SQL Proxy 連線
    "port": "5433"
}

def get_text_embedding(text: str) -> np.ndarray:
    """
    使用 Google Vertex AI 取得文本的嵌入向量 (768 維).
    
    Args:
        text (str): 要轉換的文本
    Returns:
        np.ndarray: 768 維嵌入向量
    """
    # 取得嵌入
    response = embedding_model.get_embeddings([text])

    # 提取向量
    embedding_vector = response[0].values  
    embedding_array = np.array(embedding_vector)  # 轉換為 NumPy 陣列

    return embedding_array  # 返回 768 維的 NumPy 向量

def insert_embedding(text: str):
    """
    取得文本的嵌入向量，並插入到 documents 資料表中。
    
    Args:
        text (str): 要嵌入的文本內容。
    """
    # 連接 Cloud SQL
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    try:
        # 取得 Google Vertex AI 產生的嵌入向量
        embedding_array = get_text_embedding(text)

        # 確保格式符合 PostgreSQL `vector(768)`
        embedding_list = embedding_array.tolist()

        # 插入資料到 `documents` 表
        cur.execute("""
            INSERT INTO documents (original_text, embedding)
            VALUES (%s, %s);
        """, (text, embedding_list))

        conn.commit()  # 確保數據提交
        print("✅ 成功插入嵌入向量！")

    except Exception as e:
        print(f"❌ 插入失敗: {e}")

    finally:
        cur.close()
        conn.close()


def fetch_all_documents():
    """
    查詢 `documents` 表中的所有資料，並顯示 ID、原始文本、處理後文本、嵌入向量（前 10 維）、建立時間。
    
    Returns:
        list: 包含所有查詢結果的列表，每個元素是 (id, original_text, processed_text, embedding_list, created_at)
    """
    # 連接 PostgreSQL
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    try:
        # 查詢所有數據
        cur.execute("SELECT id, original_text, processed_text, embedding, created_at FROM documents;")
        rows = cur.fetchall()  # 取得所有資料

        # 格式化結果
        results = []
        for row in rows:
            doc_id = row[0]
            original_text = row[1]
            processed_text = row[2] if row[2] is not None else "無"  # 如果為 NULL，顯示 "無"
            embedding_str = row[3]  # 768 維向量 (pgvector)
            created_at = row[4]  # 建立時間
            
            # 解析 pgvector 向量
            if embedding_str:
                try:
                    embedding = ast.literal_eval(embedding_str)  # 解析成 list of float
                    if isinstance(embedding, list):
                        embedding_preview = embedding[:10]  # 取前 10 維
                    else:
                        embedding_preview = "❌ 解析錯誤"
                except:
                    embedding = []
                    embedding_preview = "❌ 解析錯誤"
            else:
                embedding = []
                embedding_preview = "❌ 無向量"

            # 只顯示前 10 維
            embedding_preview = embedding[:10] if embedding else []

            print(f"🆔 ID: {doc_id}")
            print(f"📄 原始文本: {original_text[:50]}...")  # 顯示前 50 個字
            print(f"📝 處理後文本: {processed_text[:50]}..." if processed_text != "無" else "📝 處理後文本: 無")
            print(f"🧬 嵌入向量（前10維）: {embedding_preview} ...")
            print(f"📅 建立時間: {created_at}\n")

            results.append((doc_id, original_text, processed_text, embedding, created_at))

        return results  # 返回所有數據

    except Exception as e:
        print(f"❌ 查詢失敗: {e}")
        return []

    finally:
        cur.close()
        conn.close()


def find_top_similar_documents(query_text: str, top_k: int = 3):
    """
    利用 pgvector 找到與 `query_text` 相似度最高的前 `top_k` 筆資料。
    
    Args:
        query_text (str): 要查詢相似度的文本
        top_k (int): 要返回的相似結果數量 (預設 3)
    
    Returns:
        list: 最相似的 `top_k` 筆結果，每個元素包含 (original_text, processed_text, similarity_score)
    """
    # 取得查詢文本的嵌入向量
    query_embedding = get_text_embedding(query_text).tolist()

    # 連接 PostgreSQL
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    try:
        # 查詢最相似的前 `top_k` 筆資料
        cur.execute("""
            SELECT original_text, processed_text, embedding <=> %s::vector(768) AS similarity
            FROM documents
            ORDER BY similarity ASC
            LIMIT %s;
        """, (query_embedding, top_k))

        rows = cur.fetchall()  # 取得查詢結果

        results = []
        for row in rows:
            original_text = row[0]
            processed_text = row[1] if row[1] is not None else "無"
            similarity_score = row[2]  # 相似度分數 (越小越相似)

            print(f"📄 原始文本: {original_text[:50]}...")
            print(f"📝 處理後文本: {processed_text[:50]}..." if processed_text != "無" else "📝 處理後文本: 無")
            print(f"🎯 相似度分數: {similarity_score:.4f}")
            print("──────────────────────────")

            results.append((original_text, processed_text, similarity_score))

        return results  # 返回最相似的 `top_k` 筆結果

    except Exception as e:
        print(f"❌ 查詢失敗: {e}")
        return []

    finally:
        cur.close()
        conn.close()



# 測試插入文本
# text_input = """DDR Ratio（Double Data Rate Ratio） 是用來衡量記憶體（RAM）運作效率的一個關鍵指標，特別是在計算機系統和嵌入式設備中。DDR 記憶體技術（如 DDR3、DDR4、DDR5）通過雙倍數據速率傳輸來提高存取效率，使得數據在時脈 信號的上升與下降沿皆可傳輸，提高總體的資料吞吐量。

# DDR Ratio 通常指的是記憶體的時脈頻率（Clock Speed）與實際數據傳輸速率（Data Rate）之間的比率。例如：

# 在 DDR4-3200 記憶體中，時脈頻率為 1600 MHz，但由於 DDR 技術採用雙倍數據傳輸，實際的數據速率為 3200 MT/s（Mega Transfers per second），因此 DDR Ratio 通常表示為 2:1。
# 對於 DDR5 記憶體，隨著技術進步，數據傳輸效率進一步提升，但仍然保持相似的比例關係。
# 在效能測試或超頻調校時，DDR Ratio 可能影響系統穩定性與頻寬表現，因此調整記憶體參數時需要考量此比例，以確保最佳的運行效能和穩定性。"""
# insert_embedding(text_input)

#查詢所有文檔
# fetch_all_documents()

# # 查詢相似文檔
# query_text = """"""
# find_top_similar_documents(query_text, top_k=3)
