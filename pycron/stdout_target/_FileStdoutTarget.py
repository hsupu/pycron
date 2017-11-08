import os

from typing import Mapping

from . import StdoutTarget


class FileStdoutTarget(StdoutTarget):
    def __init__(self, is_stdout: bool, config: Mapping) -> None:
        self.is_stdout = is_stdout

    def openfd(self, run_id: str) -> int:
        file = os.path.join(os.curdir, 'var/run/run_%s/run.%s' % (run_id, 'out' if self.is_stdout else 'err'))
        dir = os.path.dirname(file)
        os.makedirs(dir, 0o775, exist_ok=True)
        return os.open(file, os.O_WRONLY | os.O_CREAT)
