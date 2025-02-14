import os
from realtime_translate_system.extensions import socketio
from realtime_translate_system.config import Language
from .speech_recongizer import SpeechRecognizer
from .transcript_service import TranscriptService
from .meeting_service import MeetingProcessor


class AudioService:
    def __init__(
        self,
        upload_folder,
        recognizer: SpeechRecognizer,
        transcript_service: TranscriptService,
        meeting_processor: MeetingProcessor,
    ):
        self.upload_folder = upload_folder
        self.recognizer: SpeechRecognizer = recognizer
        self.transcript_service: TranscriptService = transcript_service
        self.meeting_processor: MeetingProcessor = meeting_processor

        self.transcript_text = ""

    def process_audio(self, filename):
        filepath = os.path.join(self.upload_folder, filename)

        def callback(text):
            data = self.transcript_service.process(text)
            if data is not None:
                self.transcript_text += data["text"][Language.TW]["value"]
                socketio.emit("transcript", data, namespace="/audio_stream")

        self.recognizer.transcribe(filepath, callback)
        title, keywords = self.meeting_processor.gen_title_keywords(
            self.transcript_text
        )
        socketio.emit(
            "transcript",
            {"status": "complete", "title": title, "keywords": keywords},
            namespace="/audio_stream",
        )
