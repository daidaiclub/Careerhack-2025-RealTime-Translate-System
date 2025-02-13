from vertexai.generative_models import GenerativeModel
from vertexai.language_models import TextEmbeddingModel 
import json

class LLMService:
    """負責 LLM 相關操作"""
    def __init__(self, model_name):
        """初始化時提供一個 LLM 模型"""
        self.llm_model = GenerativeModel(model_name)

    def query(self, prompt: str) -> str:
        response = self.llm_model.generate_content(prompt)
        return response.text.strip()

    def parse_json_response(self, response_text):
        """嘗試解析 JSON，若解析失敗則請 LLM 修正"""
        try:
            return json.loads(response_text.strip())  # 嘗試解析 JSON
        except json.JSONDecodeError:
            print("JSON 解析錯誤，嘗試讓 LLM 修正格式...")

            fix_prompt = f"""
            Your previous response contained formatting errors. Your task is to **fix the JSON formatting** and return a correctly formatted JSON object.

            ### **Instructions:**
            - Ensure the response is **valid JSON**.
            - **Do NOT include Markdown formatting (e.g., ` ```json `).**
            - **Do NOT include any explanations or extra text.**
            - **Only return the corrected JSON object.**

            ### **Incorrect JSON Output:**
            {response_text.strip()}

            ### **Corrected JSON Output:**
            """

            fixed_response = self.query(fix_prompt)

            try:
                return json.loads(fixed_response.text.strip())  # 再次嘗試解析 JSON
            except json.JSONDecodeError:
                print("LLM 修正 JSON 仍然失敗，回傳預設值")
                return {"date": None, "keywords": []}  # 預設回應


class EmbeddingService:
    """負責嵌入向量計算"""
    def __init__(self, model_name):
        """初始化時提供一個嵌入向量模型"""
        self.embedding_model = TextEmbeddingModel.from_pretrained(model_name)
 
    def get_embedding(self, text: str, output_dim=768):
        if isinstance(text, str):
            text = [text]
        embedding = self.embedding_model.get_embeddings(text, output_dimensionality=output_dim)
        return embedding[0].values