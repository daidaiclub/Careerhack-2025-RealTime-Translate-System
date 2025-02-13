import psycopg2
import numpy as np
from vertexai.language_models import TextEmbeddingModel
import ast
from typing import List, Dict, Any
from realtime_translate_system.services.ai_service import  EmbeddingService

# PostgreSQL 連線設定
DB_CONFIG = {
    "dbname": "meetings_db",
    "user": "postgres",
    "password": "postgres",
    "host": "127.0.0.1",  # Cloud SQL Proxy 連線
    "port": "5433"
}

class Document:
    def __init__(self, doc_id, title, created_at, update_time, content, embedding, keywords, similarity=None):
        self.id = doc_id
        self.title = title
        self.created_at = created_at
        self.update_time = update_time
        self.content = content
        self.embedding = embedding
        self.keywords = keywords
        self.similarity = similarity
    
    def __str__(self):
        return f"Document(id={self.id}, title={self.title}, created_at={self.created_at}, update_time={self.update_time}, content={self.content[:50]}..., keywords={self.keywords}, similarity={self.similarity}), embedding={self.embedding[:10]}..."


class DatabaseService:
    def __init__(self, embedding_service: EmbeddingService):
        """初始化資料庫連線"""
        self.conn = psycopg2.connect(**DB_CONFIG)
        self.embedding_service = embedding_service
        self.cur = self.conn.cursor()
    
    def __del__(self):
        """物件被銷毀時關閉連線"""
        self.cur.close()
        self.conn.close()
    
    def get_text_embedding(self, text: str) -> np.ndarray:
        """使用 Google Vertex AI 取得文本的嵌入向量 (768 維)"""
        return np.array(self.embedding_service.get_embedding(text))
    
    def get_meetings(self) -> List[Document]:
        """獲取所有會議記錄"""
        try:
            self.cur.execute("SELECT id, title, created_at, update_time, content, embedding, keywords FROM documents;")
            rows = self.cur.fetchall()
            return [Document(row[0], row[1], row[2], row[3], row[4], row[5], row[6]) for row in rows]
        except Exception as e:
            print(f"❌ 查詢失敗: {e}")
            return []

    def search_meetings(self, query_embedding: List[float], top_k: int = 5) -> List[Document]:
        """透過關鍵字搜尋會議記錄，返回 `top_k` 筆結果，並包含所有欄位"""
        try:
            self.cur.execute("""
                SELECT id, title, created_at, update_time, content, embedding, keywords, embedding <=> %s::vector(768) AS similarity
                FROM documents
                ORDER BY similarity ASC
                LIMIT %s;
            """, (query_embedding, top_k))
            rows = self.cur.fetchall()
            return [Document(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]) for row in rows]
        except Exception as e:
            print(f"❌ 查詢失敗: {e}")
            return []

    def save_meeting(self, title: str, transcript: str, keywords: List[str]):
        """儲存新的會議記錄，created_at 自動設定"""
        try:
            embedding_array = self.get_text_embedding(transcript)
            embedding_list = embedding_array.tolist()
            self.cur.execute("""
                INSERT INTO documents (title, content, embedding, keywords)
                VALUES (%s, %s, %s, %s);
            """, (title, transcript, embedding_list, keywords))
            self.conn.commit()
            print("✅ 成功儲存會議記錄！")
        except Exception as e:
            print(f"❌ 儲存失敗: {e}")

    def update_meeting(self, doc_id: int, title: str, transcript: str, keywords: List[str]):
        """更新會議記錄，並自動更新 update_time"""
        try:
            embedding_array = self.get_text_embedding(transcript)
            embedding_list = embedding_array.tolist()
            self.cur.execute("""
                UPDATE documents
                SET title = %s, content = %s, embedding = %s, keywords = %s, update_time = NOW()
                WHERE id = %s;
            """, (title, transcript, embedding_list, keywords, doc_id))
            self.conn.commit()
            print("✅ 成功更新會議記錄！")
        except Exception as e:
            print(f"❌ 更新失敗: {e}")



if __name__ == "__main__":
    db_service = DatabaseService()
    
    # print("🔹 測試 save_meeting")
    # db_service.save_meeting("會議3", "每天學習一點新知識，長期下來會帶來意想不到的收穫。", ["AI", "科技"])
    
    # print("🔹 測試 get_meetings")
    # meetings = db_service.get_meetings()
    # for meeting in meetings:
    #     print(meeting)
    
    # print("🔹 測試 update_meeting")
    # db_service.update_meeting(1, "更新後的會議1", "這是更新後的內容", ["AI", "數據"])
    
    print("🔹 測試 search_meetings")
    query_embedding = "全球暖化"
    query_embedding = db_service.get_text_embedding(query_embedding)
    results = db_service.search_meetings(query_embedding.tolist(), top_k=3)
    for result in results:
        print(result)
    




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
