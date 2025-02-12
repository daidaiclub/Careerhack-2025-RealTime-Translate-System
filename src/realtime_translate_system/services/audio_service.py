import os
from realtime_translate_system.extensions import socketio
from .speech_recongizer import SpeechRecognizer
from .translation_service import TranslationService
from .term_matcher import TermMatcher

class AudioService:
    def __init__(
        self,
        upload_folder,
        recognizer: SpeechRecognizer,
        translation_service: TranslationService,
        term_matcher: TermMatcher,
    ):
        self.upload_folder = upload_folder
        self.recognizer = recognizer
        self.translation_service = translation_service
        self.term_matcher = term_matcher

    def process_audio(self, filename):
        filepath = os.path.join(self.upload_folder, filename)

        def callback(text):
            if text.strip() == "":
                return
            text = self.translation_service.translate(text)
            text = self.term_matcher.process_multilingual_text(text)
            data = {"status": "continue", "text": text}
            socketio.emit("transcript", data)

        self.recognizer.transcribe(filepath, callback)
        socketio.emit("transcript", {"status": "complete"})
