from typing import Mapping
import threading

from . import RunIdGenerator


class MemoryRunIdGenerator(RunIdGenerator):
    def __init__(self, config: Mapping) -> None:
        self.lock = threading.Lock()
        self.id = 0

    def generate(self) -> str:
        self.lock.acquire()
        try:
            self.id += 1
            return str(self.id)
        finally:
            self.lock.release()
