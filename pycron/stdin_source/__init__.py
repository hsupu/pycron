from ..const import ConstantEnum, Constant
from ._StdinSource import StdinSource
from ._FileStdinSource import FileStdinSource


class StdinSourceType(ConstantEnum):
    NONE = Constant("NONE")
    FILE = Constant("FILE")
