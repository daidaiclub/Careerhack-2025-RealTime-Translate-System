from abc import ABC, abstractmethod
from typing import List
import numpy as np
from realtime_translate_system.services.embedding import EmbeddingService

class DatabaseService(ABC):
    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service

    def get_text_embedding(self, text: str) -> np.ndarray:
        return np.array(self.embedding_service.get_embedding(text))

    @abstractmethod
    def insert_document(self, title: str, transcript_chinese: str, transcript_english: str,
                       transcript_german: str, transcript_japanese: str, keywords: list) -> int:
        pass

    @abstractmethod
    def get_document(self, doc_id: int):
        pass

    @abstractmethod
    def get_documents(self) -> List[dict]:
        pass

    @abstractmethod
    def search_documents(self, query_embedding: List[float], top_k: int = 5) -> List[dict]:
        pass

    @abstractmethod
    def update_document(self, doc_id: int, title: str, transcript_chinese: str,
                       transcript_english: str, transcript_german: str,
                       transcript_japanese: str, keywords: list) -> bool:
        pass