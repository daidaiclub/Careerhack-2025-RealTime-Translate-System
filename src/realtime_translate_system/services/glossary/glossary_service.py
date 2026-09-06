from abc import ABC, abstractmethod

class GlossaryService(ABC):
    def __init__(self):
        self.term_dicts = {}
    
    @abstractmethod
    def process_text(self, input_text: str, lang: str = None):
        pass
    
    @abstractmethod
    def process_multilingual_text(self, text_dict: dict):
        pass
    