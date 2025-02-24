import numpy as np
from typing import List
from realtime_translate_system.models.doc import Doc
from realtime_translate_system.models import db
from sqlalchemy import text, desc
from datetime import datetime
from database_service import DatabaseService

class SQLAlchemyDatabaseService(DatabaseService):
    def insert_document(
        self,
        title: str,
        transcript_chinese: str,
        transcript_english: str,
        transcript_german: str,
        transcript_japanese: str,
        keywords: list,
    ):
        """插入新的會議記錄"""
        try:
            embedding_array = self.get_text_embedding(transcript_chinese)
            embedding_list = (
                embedding_array.tolist()
            )  #  轉換為 Python List，才能存入 SQLAlchemy

            # 🔹 **SQL 插入語句**
            sql = text(
                """
                INSERT INTO documents (
                    title, transcript_chinese, transcript_english, 
                    transcript_german, transcript_japanese, embedding, keywords
                ) VALUES (
                    :title, :transcript_chinese, :transcript_english,
                    :transcript_german, :transcript_japanese, :embedding, :keywords
                ) RETURNING id;
            """
            )

            # 🔹 **執行 SQL 插入**
            result = db.session.execute(
                sql,
                {
                    "title": title,
                    # "created_at": datetime.now(),
                    # "updated_at": datetime.now(),
                    "transcript_chinese": transcript_chinese,
                    "transcript_english": transcript_english,
                    "transcript_german": transcript_german,
                    "transcript_japanese": transcript_japanese,
                    "embedding": embedding_list,
                    "keywords": keywords,
                },
            )

            db.session.commit()

            new_id = result.fetchone()[0]  # 取得新插入的 ID
            return new_id  # 返回插入的對象 ID

        except Exception as e:
            print(f"❌ 插入失敗: {e}")
            db.session.rollback()
            return None

        except Exception as e:
            db.session.rollback()
            print(f"插入失敗: {e}")
            return None

    def get_document(self, doc_id: int) -> Doc:
        """獲取 `documents` 表中的一筆資料，並返回字典包含內容與 `type()`"""
        try:
            document = db.session.query(Doc).filter_by(id=doc_id).first()

            if document:
                # meeting_data = {}
                # print("📄 會議記錄內容：")
                # for column in Doc.__table__.columns:
                #     value = getattr(meeting, column.name)
                #     meeting_data[column.name] = {"value": value, "type": type(value).__name__}
                #     print(f"{column.name}: {value} (type: {type(value).__name__})")
                return document
            else:
                print("沒有找到任何會議記錄。")
                return None

        except Exception as e:
            db.session.rollback()
            print(f"❌ 查詢失敗: {e}")
            return None

    def get_documents(self) -> List[Doc]:
        """獲取所有會議記錄"""
        # try:
        #     self.cur.execute("SELECT id, title, created_at, updated_at, content, embedding, keywords FROM Docs;")
        #     rows = self.cur.fetchall()
        #     return [Doc(row[0], row[1], row[2], row[3], row[4], row[5], row[6]) for row in rows]
        # except Exception as e:
        #     print(f"查詢失敗: {e}")
        #     return []
        try:
            return Doc.query.order_by(desc(Doc.updated_at)).all()
        except Exception as e:
            print(f"查詢失敗: {e}")
            return []


    def search_documents(
        self, query_embedding: List[float], top_k: int = 5
    ) -> List[Doc]:
        """透過關鍵字搜尋會議記錄，返回 `top_k` 筆結果，並包含所有欄位"""
        # try:
        #     self.cur.execute("""
        #         SELECT id, title, created_at, updated_at, content, embedding, keywords, embedding <=> %s::vector(768) AS similarity
        #         FROM Docs
        #         ORDER BY similarity ASC
        #         LIMIT %s;
        #     """, (query_embedding, top_k))
        #     rows = self.cur.fetchall()
        #     return [Doc(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]) for row in rows]
        # except Exception as e:
        #     print(f"查詢失敗: {e}")
        #     return []
        # 🔹 修正 SQL 查詢，移除 `content` 並確保 `similarity` 排序
        try:
            sql = text(
                """
                SELECT id, title, created_at, updated_at, transcript_chinese, transcript_english, 
                        transcript_german, transcript_japanese, embedding, keywords
                FROM documents
                ORDER BY embedding <=> (:query_embedding)::vector(768) ASC
                LIMIT :top_k;
            """
            )

            # 🔹 執行查詢
            result = (
                db.session.execute(
                    sql, {"query_embedding": query_embedding, "top_k": top_k}
                )
                .mappings()
                .all()
            )

            # #  檢查是否有結果
            # if not result:
            #     print("⚠️ 沒有找到符合的會議記錄")
            #     return []

            # #  輸出每一筆查詢結果
            # print("📌 會議記錄查詢結果：")
            # for i, row in enumerate(result):
            #     print(f"\n🔹 會議 {i + 1}:")
            #     for key, value in row.items():
            #         print(f"  {key}: {value} (type: {type(value).__name__})")

            return [Doc(**row) for row in result]

        except Exception as e:
            print(f"❌ 查詢失敗: {e}")
            db.session.rollback()
            return []

    def update_document(
        self,
        doc_id: int,
        title: str,
        transcript_chinese: str,
        transcript_english: str,
        transcript_german: str,
        transcript_japanese: str,
        keywords: list,
    ):
        """更新會議記錄，並自動更新 updated_at"""
        try:
            doc = db.session.query(Doc).filter_by(id=doc_id).first()

            if not doc:
                print(f"更新失敗 找不到 ID {doc_id} 的記錄")
                return False

            doc.title = title
            doc.transcript_chinese = transcript_chinese
            doc.transcript_english = transcript_english
            doc.transcript_german = transcript_german
            doc.transcript_japanese = transcript_japanese
            doc.keywords = keywords
            doc.embedding = self.get_text_embedding(transcript_chinese).tolist()
            doc.updated_at = datetime.now()

            db.session.commit()
            print(f"成功更新 ID {doc_id} 的會議記錄")
            return True

        except Exception as e:
            db.session.rollback()
            print(f"更新失敗 {e}")
            return False


if __name__ == "__main__":
    from realtime_translate_system.services.embedding import VertexEmbeddingService
    embedding_service = VertexEmbeddingService("text-multilingual-embedding-002")
    db_service = DatabaseService(embedding_service=embedding_service)

    db_service.insert_document(
        title="AI 發展趨勢",
        transcript_chinese="人工智能正在快速發展，對各行各業產生深遠影響。",
        transcript_english="Artificial intelligence is rapidly evolving and has a profound impact on various industries.",
        transcript_german="Künstliche Intelligenz entwickelt sich rasant und hat tiefgreifende Auswirkungen auf verschiedene Branchen.",
        transcript_japanese="人工知能は急速に進化しており、さまざまな業界に深い影響を与えています。",
        keywords=["AI", "Machine Learning", "科技"],
    )


# 測試插入文本
# text_input = """DDR Ratio（Double Data Rate Ratio） 是用來衡量記憶體（RAM）運作效率的一個關鍵指標，特別是在計算機系統和嵌入式設備中。DDR 記憶體技術（如 DDR3、DDR4、DDR5）通過雙倍數據速率傳輸來提高存取效率，使得數據在時脈 信號的上升與下降沿皆可傳輸，提高總體的資料吞吐量。

# DDR Ratio 通常指的是記憶體的時脈頻率（Clock Speed）與實際數據傳輸速率（Data Rate）之間的比率。例如：

# 在 DDR4-3200 記憶體中，時脈頻率為 1600 MHz，但由於 DDR 技術採用雙倍數據傳輸，實際的數據速率為 3200 MT/s（Mega Transfers per second），因此 DDR Ratio 通常表示為 2:1。
# 對於 DDR5 記憶體，隨著技術進步，數據傳輸效率進一步提升，但仍然保持相似的比例關係。
# 在效能測試或超頻調校時，DDR Ratio 可能影響系統穩定性與頻寬表現，因此調整記憶體參數時需要考量此比例，以確保最佳的運行效能和穩定性。"""
# insert_embedding(text_input)

# 查詢所有文檔
# fetch_all_Docs()

# # 查詢相似文檔
# query_text = """"""
# find_top_similar_Docs(query_text, top_k=3)
