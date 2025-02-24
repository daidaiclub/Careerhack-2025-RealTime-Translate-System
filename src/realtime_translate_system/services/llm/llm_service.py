from abc import ABC, abstractmethod
import json
import re

class LLMService(ABC):
    """負責 LLM 相關操作"""

    @abstractmethod
    def query(self, prompt: str, generation_config=None) -> str:
        pass

    def parse_json_response(self, response_text: str) -> dict:
        """嘗試解析 JSON，若解析失敗則請 LLM 修正"""
        def clean_json_output(text):
            """移除 LLM 產生的 ```json 標記，返回純 JSON 字串。"""
            return re.sub(r"^```json\s*|\s*```$", "", text.strip())
    
        try:
            print("嘗試解析 JSON 失敗，請 LLM 修正")
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