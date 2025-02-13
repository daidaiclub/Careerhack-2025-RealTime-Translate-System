from typing import List, Dict, Any

class DatabaseService:

    def get_meetings(self) -> List[Dict[str, Any]]:
        """獲取所有會議記錄"""
        raise NotImplementedError

    def search_meetings(self, query_embedding: List[float]) -> List[Dict[str, Any]]:
        """透過語意相似度搜尋會議記錄"""
        raise NotImplementedError

    def save_meeting(self, title: str, date: str, transcript: str, keywords: List[str]) -> None:
        """儲存新的會議記錄"""
        raise NotImplementedError