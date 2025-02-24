from .llm_service import LLMService
from vertexai.generative_models import GenerativeModel

class VertexLLMService(LLMService):
    def __init__(self, model_name):
        """初始化時提供一個 LLM 模型"""
        self.llm_model = GenerativeModel(model_name)

    def query(self, prompt: str, generation_config=None) -> str:
        response = self.llm_model.generate_content(prompt, generation_config=generation_config)
        return response.text.strip()