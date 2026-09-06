import numpy as np
from typing import List
from realtime_translate_system.models.doc import Doc
from realtime_translate_system.models import db
from sqlalchemy import text, desc
from datetime import datetime


class DocRepository:
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
            embedding_list = embedding_array.tolist()

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

            result = db.session.execute(
                sql,
                {
                    "title": title,
                    "transcript_chinese": transcript_chinese,
                    "transcript_english": transcript_english,
                    "transcript_german": transcript_german,
                    "transcript_japanese": transcript_japanese,
                    "embedding": embedding_list,
                    "keywords": keywords,
                },
            )

            db.session.commit()

            new_id = result.fetchone()[0]
            return new_id

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
        try:
            return Doc.query.order_by(desc(Doc.updated_at)).all()
        except Exception as e:
            print(f"查詢失敗: {e}")
            return []

    def search_documents(
        self, query_embedding: List[float], top_k: int = 5
    ) -> List[Doc]:
        """透過關鍵字搜尋會議記錄，返回 `top_k` 筆結果，並包含所有欄位"""
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

            result = (
                db.session.execute(
                    sql, {"query_embedding": query_embedding, "top_k": top_k}
                )
                .mappings()
                .all()
            )

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
    db_service = DocRepository(embedding_service=embedding_service)

    db_service.insert_document(
        title="AI 發展趨勢",
        transcript_chinese="人工智能正在快速發展，對各行各業產生深遠影響。",
        transcript_english="Artificial intelligence is rapidly evolving and has a profound impact on various industries.",
        transcript_german="Künstliche Intelligenz entwickelt sich rasant und hat tiefgreifende Auswirkungen auf verschiedene Branchen.",
        transcript_japanese="人工知能は急速に進化しており、さまざまな業界に深い影響を与えています。",
        keywords=["AI", "Machine Learning", "科技"],
    )
