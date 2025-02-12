import queue
from typing import Callable

class SpeechRecognizer:
    def __init__(self, *args, **kwargs):
        pass

    def transcribe(self, audio_path: str, callback: Callable[[str], None]):
        raise NotImplementedError()
    
    def transcribe_streaming(self, audio_queue: queue.Queue, callback: Callable[[str], None], done: Callable[[], None]):
        raise NotImplementedError()