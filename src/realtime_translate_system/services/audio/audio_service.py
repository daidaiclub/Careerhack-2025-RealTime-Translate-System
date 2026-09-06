import queue
from abc import ABC, abstractmethod

class AudioService(ABC):
    @abstractmethod
    def process_audio_stream(self, audio_queue: queue.Queue):
        pass

    @abstractmethod
    def process_audio_file(self, filepath: str):
        pass
