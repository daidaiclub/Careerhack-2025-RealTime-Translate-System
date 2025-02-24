import queue
from typing import Callable
from abc import ABC, abstractmethod

class Speech2TextService(ABC):
    @abstractmethod
    def transcribe(self, audio_path: str, callback: Callable[[str], None]):
        pass

    @abstractmethod
    def transcribe_streaming(self, audio_queue: queue.Queue, callback: Callable[[str], None], done: Callable[[], None]):
        pass