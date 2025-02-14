import numpy as np
from datetime import datetime, timedelta
from fuzzywuzzy import fuzz
from realtime_translate_system.services.database_service import DatabaseService
from realtime_translate_system.services.ai_service import LLMService, EmbeddingService
from numpy.linalg import norm

class RetrievalAugmentedGeneration:
    """負責從向量資料庫檢索資訊並產生 RAG Prompt""" 
    def __init__(self, llm_service: LLMService, embedding_service: EmbeddingService, db_service: DatabaseService):
        self.llm_service = llm_service
        self.embedding_service = embedding_service
        self.db_service = db_service
     
    def parse_user_query(self, user_query: str):
        today = datetime.today().strftime("%Y-%m-%d")
        yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        prompt = f"""
        You are a highly intelligent assistant specialized in structured information extraction. Your task is to analyze the user query and extract the **meeting date (YYYY-MM-DD)** and **relevant keywords** that describe the meeting.

        ### **Instructions:**
        - Extract the meeting date from the query, if provided. Convert phrases like "today" or "yesterday" into the correct **YYYY-MM-DD** format.
            - "today" is {today}.
            - "yesterday" is {yesterday}.
        - Identify key terms that describe the meeting topic.
        - **Your response must be a valid JSON object in Traditional Chinese.**
        - **Only return the JSON object, without Markdown (` ```json `) or any explanations.**

        ### **Examples:**
        1. **User Query:** "尋找昨天有關市場分析的會議紀錄"  
        **Output:** `{{"date": "{yesterday}", "keywords": ["市場分析"]}}`

        2. **User Query:** "請幫我找 AI 技術創新相關的會議"
        **Output:** `{{"date": null, "keywords": ["AI", "技術創新"]}}`

        3. **User Query:** "今天的供應鏈管理會議內容是什麼？"
        **Output:** `{{"date": "{today}", "keywords": ["供應鏈管理"]}}`

        Now, extract the date and keywords from the following query and return only a valid JSON object in Traditional Chinese.
        **User Query:** {user_query}
        """
        
        response = self.llm_service.query(prompt)
        parsed_response = self.llm_service.parse_json_response(response)
        
        date = parsed_response.get("date", None)
        keywords = parsed_response.get("keywords", [])
        
        return date, keywords

    def fuzzy_match_keywords(self, search_keywords, metadata_keywords, threshold=80):
        return any(
            fuzz.partial_ratio(k, keyword) >= threshold
            for k in search_keywords
            for keyword in metadata_keywords
        )

    def hybrid_search(self, user_query: str):
        keyword_threshold = 80
        
        search_date, search_keywords = self.parse_user_query(user_query)
        print(f'轉化後使用者的查詢:\ndate: {search_date},  keywords: {search_keywords}')

        results = self.db_service.get_meetings()

        if search_date:
            # 將 search_date 字串轉換成 date 物件
            search_date_obj = datetime.strptime(search_date, "%Y-%m-%d").date()
        else:
            search_date_obj = None

        filtered_meetings = [
            doc for doc in results if not search_date_obj or doc.created_at.date() == search_date_obj
        ]
        
        if search_keywords:
            filtered_meetings = [
                m for m in filtered_meetings if self.fuzzy_match_keywords(search_keywords,  m.keywords, keyword_threshold)
            ]
        
        if filtered_meetings:
            return filtered_meetings
        
        query_embedding = self.embedding_service.get_embedding(search_keywords)
        results = self.db_service.search_meetings(query_embedding, top_k=1)

        return results


class MeetingProcessor:
    """負責處理會議內容，包括標題、關鍵字生成與儲存"""
    def __init__(self, llm_service: LLMService, db_service: DatabaseService, embedding_service: EmbeddingService):
        self.llm_service = llm_service
        self.db_service = db_service
        self.embedding_service = embedding_service

        self.rag_service = RetrievalAugmentedGeneration(
            llm_service=self.llm_service,
            embedding_service=self.embedding_service,
            db_service=self.db_service,
        ) 
    
    def gen_title_keywords(self, transcript):
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
    
    def _is_retrieval_query(self, user_query):
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

    def gen_meeting_summarize(self, user_query: str):
        """根據查詢出的會議資訊，生成 RAG Prompt，讓 LLM 完成使用者的需求"""

        retrieved_meetings = self.rag_service.hybrid_search(user_query)
        
        if self._is_retrieval_query(user_query):
            print(retrieved_meetings)
            return [meeting.to_dict() for meeting in retrieved_meetings]
        
        meetings_context = "\n\n".join([
            f"**Meeting Title:** {meeting.title}\n"
            f"**Create Date:** {meeting.created_at}\n"
            f"**Transcript:** {meeting.transcript_chinese}"  # 限制最大 500 字
            for meeting in retrieved_meetings
        ])

        prompt = f"""
        You are an AI assistant specializing in summarizing meeting records. Your task is to read the given meeting transcripts and generate **separate, paragraph-style summaries** for each meeting in **Traditional Chinese**.

        ### **Meeting Records**
        {meetings_context}

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