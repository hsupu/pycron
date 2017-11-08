class RunIdGenerator(object):
    def close(self):
        pass

    def generate(self) -> str:
        raise NotImplementedError()
