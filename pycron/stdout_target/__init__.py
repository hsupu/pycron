from ..const import ConstantEnum, Constant
from ._StdoutTarget import StdoutTarget
from ._FileStdoutTarget import FileStdoutTarget


class StdoutTargetType(ConstantEnum):
    NONE = Constant("NONE")
    FILE = Constant("FILE")
