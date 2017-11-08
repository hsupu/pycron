from ..const import ConstantEnum, Constant
from ._RunIdGenerator import RunIdGenerator
from ._MemoryRunIdGenerator import MemoryRunIdGenerator
from ._FileRunIdGenerator import FileRunIdGenerator


class RunIdGeneratorType(ConstantEnum):
    MEMORY = Constant("MEMORY")
    FILE = Constant("FILE")
