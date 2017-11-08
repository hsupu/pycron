class StdoutTarget(object):
    def openfd(self, run_id: str) -> int:
        raise NotImplementedError()
