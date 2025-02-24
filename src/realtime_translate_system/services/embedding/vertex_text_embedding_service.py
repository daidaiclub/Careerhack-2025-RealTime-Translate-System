from embedding_service import EmbeddingService
from vertexai.language_models import TextEmbeddingModel 

class VertexEmbeddingService(EmbeddingService):
    """負責嵌入向量計算"""
    def __init__(self, model_name):
        """初始化時提供一個嵌入向量模型"""
        self.embedding_model = TextEmbeddingModel.from_pretrained(model_name)
 
    def get_embedding(self, text: str, output_dim=768):
        if isinstance(text, str):
            text = [text]
        embedding = self.embedding_model.get_embeddings(text, output_dimensionality=output_dim)
        return embedding[0].values