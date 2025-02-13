import os
from realtime_translate_system.extensions import socketio
from .speech_recongizer import SpeechRecognizer
from .translation_service import TranslationService
from .term_matcher import TermMatcher


class AudioService:
    def __init__(
        self,
        upload_folder,
        recognizer,
        translation_service,
        term_matcher,
    ):
        self.upload_folder = upload_folder
        self.recognizer: SpeechRecognizer = recognizer
        self.translation_service: TranslationService = translation_service
        self.term_matcher: TermMatcher = term_matcher

    def process_audio(self, filename):
        filepath = os.path.join(self.upload_folder, filename)

        def callback(text):
            if text.strip() == "":
                return
            text = self.translation_service.translate(text)
            multilingual_text = self.term_matcher.process_multilingual_text(text)
            data = {"status": "continue", "text": multilingual_text}
            socketio.emit("transcript", data, namespace="/audio_stream")

        self.recognizer.transcribe(filepath, callback)
        socketio.emit("transcript", {"status": "complete"}, namespace="/audio_stream")
