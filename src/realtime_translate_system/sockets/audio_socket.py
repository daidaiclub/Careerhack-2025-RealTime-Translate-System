from flask_socketio import SocketIO, Namespace
import queue
from realtime_translate_system.services.audio import AudioService


class AudioNamespace(Namespace):
    def __init__(
        self,
        namespace,
        socketio: SocketIO,
        audio_service: AudioService,
    ):
        super().__init__(namespace)
        self.audio_queue = queue.Queue()
        self.socketio = socketio
        self.audio_service = audio_service

    def on_audio_stream(self, data: dict):
        """
        處理 WebSocket 傳入的音頻流
        """
        try:
            status = data.get("status")
            audio_chunk = data.get("audio_chunk")

            if status == "start":
                self.audio_queue.queue.clear()
                self.socketio.start_background_task(
                    self.audio_service.process_audio_stream,
                    self.audio_queue,
                )

            self.audio_queue.put(audio_chunk)
        except Exception as e:
            print(f"❌ Error processing audio stream: {e}")


def init_socketio(
    socketio: SocketIO,
    audio_service: AudioService,
): 
    socketio.on_namespace(
        AudioNamespace(
            "/audio_stream",
            socketio,
            audio_service,
        )
    )
