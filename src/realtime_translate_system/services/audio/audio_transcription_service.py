import queue
from realtime_translate_system.config import Language
from realtime_translate_system.extensions import socketio
from realtime_translate_system.services.audio import AudioService
from realtime_translate_system.services.document import DocService
from realtime_translate_system.services.speech import Speech2TextService
from realtime_translate_system.services.translation import TranslationService
from realtime_translate_system.services.glossary import GlossaryService


class AudioTranscriptionService(AudioService):
    def __init__(
        self,
        recognizer: Speech2TextService,
        glossary_service: GlossaryService,
        translation_service: TranslationService,
        doc_processor: DocService,
    ):
        self.namespace = "/audio_service"
        self.recognizer: Speech2TextService = recognizer
        self.doc_processor: DocService = doc_processor
        self.glossary_service: GlossaryService = glossary_service
        self.translation_service: TranslationService = translation_service

        self.previous_translation = None
        self.transcript_text = ""

    def process_transcript(self, text, event: str):
        translated_text = self.translation_service.translate(
            content=text,
            previous_translation=self.previous_translation,
            term_dict=self.glossary_service.term_dicts,
        )
        processed_text = self.glossary_service.process_multilingual_text(
            translated_text
        )
        self.previous_translation = translated_text
        data = {"status": "continue", "text": processed_text}
        if data is not None:
            self.transcript_text += data["text"][Language.TW]["value"]
            socketio.emit(event, data, namespace=self.namespace)

    def process_transcript_complete(self, event: str):
        title, keywords = self.doc_processor.gen_title_keywords(self.transcript_text)
        data = {"status": "complete", "title": title, "keywords": keywords}
        socketio.emit(event, data, namespace=self.namespace)

    def process_audio_stream(self, audio_queue: queue.Queue):
        def callback(text: str):
            self.process_transcript(text, "transcript_stream")

        def done():
            self.process_transcript_complete("transcript_stream")

        self.recognizer.transcribe_streaming(audio_queue, callback, done)

    def process_audio_file(self, filepath: str):
        def callback(text: str):
            self.process_transcript(text, "transcript_aduio_file")

        self.recognizer.transcribe(filepath, callback)
        self.process_transcript_complete("transcript_audio_file")
