from vertexai.generative_models import GenerativeModel
from vertexai.language_models import TextEmbeddingModel 
import json
import re

class LLMService:
    """負責 LLM 相關操作"""
    def __init__(self, model_name):
        """初始化時提供一個 LLM 模型"""
        self.llm_model = GenerativeModel(model_name)

    def query(self, prompt: str, generation_config=None) -> str:
        response = self.llm_model.generate_content(prompt, generation_config=generation_config)
        return response.text.strip()

    def parse_json_response(self, response_text):
        """嘗試解析 JSON，若解析失敗則請 LLM 修正"""
        def clean_json_output(text):
            """移除 LLM 產生的 ```json 標記，返回純 JSON 字串。"""
            return re.sub(r"^```json\s*|\s*```$", "", text.strip())
    
        try:
            cleaned_output = clean_json_output(response_text)
            return json.loads(cleaned_output.strip())

        except json.JSONDecodeError:

            fix_prompt = f"""
            Your previous response contained formatting errors. Your task is to **fix the JSON formatting** 
            and return a correctly formatted JSON object enclosed within a valid Markdown `json` code block.

            ### **Instructions:**
            - Ensure the response is **valid JSON**.
            - **Your output must start with ```json and end with ```**.
            - **Do NOT include any explanations or extra text.**
            - **Only return the corrected JSON object in the required format.**

            ### **Incorrect JSON Output:**
            {response_text.strip()}

            ### **Corrected JSON Output:**
            ```json
            """

            fixed_response_text = self.query(fix_prompt)

            try:
                cleaned_output = clean_json_output(fixed_response_text)
                return json.loads(cleaned_output.strip())
            
            except json.JSONDecodeError:
                print("LLM 修正 JSON 仍然失敗，回傳預設值")
                return {}


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