from typing import List
from .translation_service import TranslationService
from .term_matcher import TermMatcher

class TranscriptService:
    def __init__(self, glossary_folder: List, translation_service: TranslationService, term_matcher: TermMatcher):
        self.translation_service = translation_service
        self.term_matcher = term_matcher

        self.previous_translation_text = None
        self.term_list = self.translation_service.load_term_dict(glossaries_paths=glossary_folder)

    def process(self, text):
        if text.strip() == "":
            return None

        text = self.translation_service.translate(text, previous_translation_text=self.previous_translation_text, term_list=self.term_list)

        multilingual_text = self.term_matcher.process_multilingual_text(text)
        data = {"status": "continue", "text": multilingual_text}
        return data