from abc import ABC, abstractmethod

class GlossaryService(ABC):
    @abstractmethod
    def load_term_dict(self, glossaries_path="", glossaries_paths=[]) -> str:
        pass
    
    @abstractmethod
    def process_text(self, input_text: str, lang: str = None):
        pass
    
    @abstractmethod
    def process_multilingual_text(self, text_dict: dict):
        pass
    