import os

from typing import Mapping

from . import StdinSource


class FileStdinSource(StdinSource):
    def __init__(self, config: Mapping) -> None:
        self.file = config['file']  # type: str

    def openfd(self) -> int:
        return os.open(self.file, os.O_RDONLY)
