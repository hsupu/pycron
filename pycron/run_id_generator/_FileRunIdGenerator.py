from typing import Mapping
import fcntl

from . import RunIdGenerator


class FileRunIdGenerator(RunIdGenerator):
    def __init__(self, config: Mapping) -> None:
        self.filename = config['file']
        self.fd = open(self.filename)
        fcntl.flock(self.fd, fcntl.LOCK_EX)

    def close(self):
        fcntl.flock(self.fd, fcntl.LOCK_UN)

    def generate(self) -> str:
        pass
