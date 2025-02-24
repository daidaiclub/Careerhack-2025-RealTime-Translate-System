import numpy as np
from realtime_translate_system.models.doc import Doc
from realtime_translate_system.services.database import DatabaseService
from llm.llm_service import LLMService
from embedding.embedding_service import EmbeddingService
from numpy.linalg import norm
from abc import ABC, abstractmethod

class DocService(ABC):
    """定義會議處理的基本接口。"""
    def __init__(self, llm_service: LLMService, embedding_service: EmbeddingService, db_service: DatabaseService):
        self.llm_service = llm_service
        self.embedding_service = embedding_service
        self.db_service = db_service
        
    def gen_title_keywords(self, transcript: str) -> tuple[str, list[str]]:
        prompt=f"""You are a highly intelligent assistant specialized in structured information extraction. Your task is to analyze a meeting transcript and generate a **title** that summarizes the meeting content. Then, based on the title and transcript, extract **relevant keywords**.

        ### **Instructions:**
        1. **Step 1: Generate a Meeting Title**
            - Carefully read the provided meeting transcript.
            - Summarize the main topic of the meeting in a concise yet informative title.
            - The title should be in Traditional Chinese.

        2. **Step 2: Extract Relevant Keywords**
            - Identify key terms that best represent the content of the meeting.
            - Extract important concepts, topics, names, or technical terms mentioned in the transcript.
            - Provide at least 3 and at most 8 keywords.

        3. **Output Format**
            - Your response **must be enclosed within ```json and ```**.
            - **Do not include any explanations, only return the JSON object**.
            - The JSON format must strictly follow this structure:

        ### **Example Output:**
        
        ```json
        {{
            "title": "人工智慧在醫療產業的應用與挑戰",
            "keywords": ["人工智慧", "醫療科技", "機器學習", "數據分析", "醫療影像"]
        }}
        ```

        Now, analyze the following meeting transcript and return only a valid JSON object enclosed within ```json and ```.
        
        Meeting Transcript:
        {transcript}
        """
        
        generation_config = {
            "candidate_count": 1,
            "max_output_tokens": 100,
            "temperature": 0.8,
            "top_p": 0.85,
            "top_k": 30,
        }

        response = self.llm_service.query(prompt, generation_config)
        parsed_response = self.llm_service.parse_json_response(response)
        
        title = parsed_response.get("title", "未命名會議")
        keywords = parsed_response.get("keywords", [])
        
        return title, keywords
    
    def is_retrieval_query(self, user_query):
        """
        判斷使用者的查詢是要「找出會議」還是「總結會議」。
        """

        # 定義「找出會議」與「總結會議」的代表性描述
        retrieval_task = "搜尋找出特定主題的會議記錄"
        summarization_task = "總結與整理會議的核心結論"

        # 取得嵌入向量
        embedding_retrieval = np.array(self.embedding_service.get_embedding(retrieval_task))
        embedding_summarization = np.array(self.embedding_service.get_embedding(summarization_task))
        embedding_query = np.array(self.embedding_service.get_embedding(user_query))

        # 計算餘弦相似度
        similarity_retrieval = np.dot(embedding_retrieval, embedding_query) / (norm(embedding_retrieval) * norm(embedding_query))
        similarity_summarization = np.dot(embedding_query, embedding_summarization) / (norm(embedding_query) * norm(embedding_summarization))

        # 判斷查詢類型
        if similarity_retrieval > similarity_summarization:
            return True  # 偏向「找出會議」
        else:
            return False  # 偏向「總結會議」
    
    def gen_summarize(self, docs: list[Doc]) -> str:
        docs_context = "\n\n".join([
            f"**Meeting Title:** {doc.title}\n"
            f"**Create Date:** {doc.created_at}\n"
            f"**Transcript:** {doc.transcript_chinese}"  # 限制最大 500 字
            for doc in docs
        ])

        prompt = f"""
        You are an AI assistant specializing in summarizing meeting records. Your task is to read the given meeting transcripts and generate **separate, paragraph-style summaries** for each meeting in **Traditional Chinese**.

        ### **Meeting Records**
        {docs_context}

        ### **Instructions**
        - **Summarize each meeting separately in a single paragraph.**
        - **Ensure each summary is concise, informative, and well-structured.**
        - **Clearly distinguish between different meetings.**
        - **Write the summaries in Traditional Chinese (繁體中文).**
        
        Now, summarize each meeting separately in Traditional Chinese:
        """
        
        generation_config = {
            "candidate_count": 1,
            "max_output_tokens": 2000,
            "temperature": 0.8,
            "top_p": 0.9,
            "top_k": 40,
        }
        
        response = self.llm_service.query(prompt, generation_config)
        
        return response
    
    @abstractmethod
    def get_documents(self, user_query: str) -> list[Doc]:
        pass