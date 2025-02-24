from datetime import datetime, timedelta
from doc_service import DocService
from fuzzywuzzy import fuzz
from realtime_translate_system.models.doc import Doc

class RAGService(DocService):
    """負責從向量資料庫檢索資訊並產生 RAG Prompt""" 
    def __init__(self, llm_service, embedding_service, db_service):
        super().__init__(llm_service, embedding_service, db_service)
        
    def _parse_user_query(self, user_query: str):
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
    
    def _fuzzy_match_keywords(self, search_keywords, metadata_keywords):
        threshold=80
        
        return any(
            fuzz.partial_ratio(k, keyword) >= threshold
            for k in search_keywords
            for keyword in metadata_keywords
        )
        
    def get_documents(self, user_query: str) -> list[Doc]:
        search_date, search_keywords = self._parse_user_query(user_query)
        print(f'轉化後使用者的查詢:\ndate: {search_date},  keywords: {search_keywords}')

        results = self.db_service.get_meetings()

        search_date_obj = datetime.strptime(search_date, "%Y-%m-%d").date() if search_date else None

        filtered_meetings = [
            doc for doc in results if not search_date_obj or doc.created_at.date() == search_date_obj
        ]
        
        if search_keywords:
            filtered_meetings = [
                m for m in filtered_meetings if self._fuzzy_match_keywords(search_keywords,  m.keywords)
            ]
        
        if filtered_meetings:
            return filtered_meetings
        
        query_embedding = self.embedding_service.get_embedding(search_keywords)
        results = self.db_service.search_meetings(query_embedding, top_k=1)

        return results