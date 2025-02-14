from flask_socketio import SocketIO, Namespace
import threading
import queue
from realtime_translate_system.services import (
    SpeechRecognizer,
    TranscriptService,
    MeetingProcessor,
)


class AudioNamespace(Namespace):
    def __init__(
        self,
        namespace,
        socketio: SocketIO,
        recognizer: SpeechRecognizer,
        transcript_service: TranscriptService,
        meeting_processor: MeetingProcessor,
    ):
        super().__init__(namespace)
        self.socketio = socketio
        self.recognizer = recognizer
        self.transcript_service = transcript_service
        self.meeting_processor = meeting_processor
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
                data = self.transcript_service.process(text)
                if data is not None:
                    self.transcript_text += data["Traditional Chinese"]["value"]
                    self.emit("transcript_stream", data)

            def done():
                # generator title and keywords
                self.audio_task = None
                title, keywords = self.meeting_processor.gen_title_keywords(
                    self.transcript_text
                )
                data = {"status": "complete", "title": title, "keywords": keywords}
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
    transcript_service: TranscriptService,
    meeting_processor: MeetingProcessor,
):
    socketio.on_namespace(
        AudioNamespace("/audio_stream", socketio, recognizer, transcript_service, meeting_processor)
    )
