from abc import ABC, abstractmethod

class EmbeddingService(ABC):
    """負責嵌入向量計算"""
 
    @abstractmethod
    def get_embedding(self, text: str, output_dim :int) -> list[float]:
        pass