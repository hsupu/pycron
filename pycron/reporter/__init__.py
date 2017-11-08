from ..const import ConstantEnum, Constant
from ._Reporter import Reporter
from ._RabbitMQReporter import RabbitMQReporter


class ReporterType(ConstantEnum):
    NONE = Constant("NONE")
    RABBITMQ = Constant("RABBITMQ")

