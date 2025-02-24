from flask_socketio import SocketIO, Namespace
import threading
import queue
from realtime_translate_system.config import Language
from realtime_translate_system.services.speech import Speech2TextService
from realtime_translate_system.services.translation import TranslationService
from realtime_translate_system.services.document import DocService
from realtime_translate_system.services.glossary import GlossaryService

class AudioNamespace(Namespace):
    def __init__(
        self,
        namespace,
        socketio: SocketIO,
        speech2text_service: Speech2TextService,
        translation_service: TranslationService,
        document_service: DocService,
        glossary_service: GlossaryService
    ):
        super().__init__(namespace)
        self.socketio = socketio
        self.speech2text_service = speech2text_service
        self.translation_service = translation_service
        self.document_service = document_service
        self.glossary_service = glossary_service
        self.audio_task = None
        self.audio_queue = queue.Queue()
        self.thread_lock = threading.Lock()

        self.transcript_text = ""

    def on_audio_stream(self, data):
        """
        處理 WebSocket 傳入的音頻流
        """
        try:

            def callback(text: str):
                previous_translation = None
                glossaries_paths = None
                term_dict = self.glossary_service.load_term_dict(glossaries_paths)
                
                translated_text = self.translation_service.translate(content=text, previous_translation=previous_translation, term_dict=term_dict)
                
                processed_text  = self.glossary_service.process_multilingual_text(translated_text)
                response_payload = {"status": "continue", "text": processed_text}
                
                if response_payload is not None:
                    self.transcript_text += response_payload["text"][Language.TW]["value"]
                    self.emit("transcript_stream", response_payload)

            def done():
                # generator title and keywords
                self.audio_task = None
                title, keywords = self.document_service.gen_title_keywords(
                    self.transcript_text
                )
                data = {"status": "complete", "title": title, "keywords": keywords}
                self.emit("transcript_stream", data)

            with self.thread_lock:
                if self.audio_task is None:
                    while not self.audio_queue.empty():
                        self.audio_queue.get_nowait()

                    self.audio_task = self.socketio.start_background_task(
                        self.speech2text_service.transcribe_streaming,
                        self.audio_queue,
                        callback,
                        done,
                    )

            self.audio_queue.put(data)
        except Exception as e:
            print(f"❌ Error processing audio stream: {e}")


def init_socketio(
    socketio: SocketIO,
    speech2text_service: Speech2TextService,
    translation_service: TranslationService,
    document_service: DocService
):
    socketio.on_namespace(
        AudioNamespace("/audio_stream", socketio, speech2text_service, translation_service, document_service)
    )
