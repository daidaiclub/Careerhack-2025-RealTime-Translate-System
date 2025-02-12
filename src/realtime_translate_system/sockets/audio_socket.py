from flask_socketio import SocketIO, Namespace
import threading
import queue
from realtime_translate_system.services import SpeechRecognizer, TranslationService, TermMatcher


class AudioNamespace(Namespace):
    def __init__(
        self,
        namespace,
        socketio: SocketIO,
        recognizer: SpeechRecognizer,
        translation_service: TranslationService,
        term_matcher: TermMatcher,
    ):
        super().__init__(namespace)
        self.socketio = socketio
        self.recognizer = recognizer
        self.translation_service = translation_service
        self.term_match = term_matcher
        self.audio_task = None
        self.audio_queue = queue.Queue()
        self.thread_lock = threading.Lock()

    def on_audio_stream(self, data):
        """
        處理 WebSocket 傳入的音頻流
        """
        try:
            def callback(text: str):
                if text.strip() == "":
                    return
                text = self.translation_service.translate(text)
                text = self.term_match.process_multilingual_text(text)
                data = {"status": "continue", "text": text}
                self.emit("transcript_stream", data)

            def done():
                self.audio_task = None
                data = {"status": "complete"}
                self.emit("transcript_stream", data)

            with self.thread_lock:
                if self.audio_task is None:
                    while not self.audio_queue.empty():
                        self.audio_queue.get_nowait()

                    self.audio_task = self.socketio.start_background_task(
                        self.recognizer.transcribe_streaming,
                        self.audio_queue,
                        callback,
                        done,
                    )

            self.audio_queue.put(data)
        except Exception as e:
            print(f"❌ Error processing audio stream: {e}")


def init_socketio(
    socketio: SocketIO,
    recognizer: SpeechRecognizer,
    translation_service: TranslationService,
    term_matcher: TermMatcher,
):
    socketio.on_namespace(
        AudioNamespace("/audio_stream", socketio, recognizer, translation_service, term_matcher)
    )
