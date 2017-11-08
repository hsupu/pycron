from typing import Optional, Mapping

from crontab import CronTab

from .reporter import ReporterType, Reporter, RabbitMQReporter
from .stdin_source import StdinSourceType, StdinSource, FileStdinSource
from .stdout_target import StdoutTargetType, StdoutTarget, FileStdoutTarget

reporter_map = {
    ReporterType.NONE: None,
    ReporterType.RABBITMQ: RabbitMQReporter
}

stdin_map = {
    StdinSourceType.NONE: None,
    StdinSourceType.FILE: FileStdinSource,
}

stdout_map = {
    StdoutTargetType.NONE: None,
    StdoutTargetType.FILE: FileStdoutTarget,
}


class Task:
    def __init__(self, task_name: str, task_config: Mapping) -> None:
        self.name = task_name
        self.cron_str = task_config['cron']  # type: str
        self.cron = CronTab(self.cron_str)  # type: CronTab
        self.user = task_config['user']  # type: str
        self.group = task_config['group']  # type: str
        self.workDir = task_config['workDir']  # type: str
        self.executable = task_config['executable']  # type: str
        self.args = [x for x in task_config['args']]  # type: list
        self.env = {k: v for k, v in task_config['env'].items()}  # type: dict

        stdin_config = task_config['stdin']
        stdin_class = stdin_map[stdin_config['source']]
        self.stdin = None if stdin_class is None else stdin_class(stdin_config) \
            # type: Optional[StdinSource]

        stdout_config = task_config['stdout']
        stdout_class = stdout_map[stdout_config['target']]
        self.stdout = None if stdout_class is None else stdout_class(True, stdout_config) \
            # type: Optional[StdoutTarget]

        stderr_config = task_config['stderr']
        stderr_class = stdout_map[stderr_config['target']]
        self.stderr = None if stderr_class is None else stderr_class(False, stderr_config) \
            # type: Optional[StdoutTarget]
