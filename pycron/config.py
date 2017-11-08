import logging
import os

from typing import Optional, List, Dict, Mapping
from strictyaml import \
    load as loadyaml, \
    EmptyNone as YNone, \
    Bool as YBool, \
    Int as YInt, \
    Str as YStr, \
    Float as YFloat, \
    Map as YMap, \
    MapPattern as YMapPattern, \
    Seq as YSeq, \
    Enum as YEnum, \
    Optional as YOpt, \
    Any as YAny
from ruamel.yaml.error import YAMLError

from .run_id_generator import RunIdGeneratorType
from .reporter import ReporterType
from .stdin_source import StdinSourceType
from .stdout_target import StdoutTargetType


class ParseError(Exception):
    pass


_taskd_schema = YMap({
    "log": YMap({
        "file": YStr(),
        "level": YEnum(['DEBUG', 'INFO', 'NOTICE', 'WARN']),
    }),
    YOpt("runIdGenerator"): YMap({
        "type": YEnum(RunIdGeneratorType.entries()),
        YOpt("file"): YStr()
    }),
    YOpt("reporter"): YMap({
        "type": YEnum(ReporterType.entries()),
        YOpt("rabbitmq"): YMap({
            "uri": YStr(),
            "queue": YStr(),
        }),
    }),
})

_task_schema = YMap({
    "executable": YStr(),
    "cron": YStr(),
    YOpt("user"): YStr(),
    YOpt("group"): YStr(),
    YOpt("workDir"): YStr(),
    YOpt("env"): YMapPattern(YStr(), YStr()),
    YOpt("args"): YSeq(YStr()),
    YOpt("stdin"): YMap({
        "source": YEnum(StdinSourceType.entries()),
        YOpt("file"): YStr(),
    }),
    YOpt("stdout"): YMap({
        "target": YEnum(StdoutTargetType.entries()),
    }),
    YOpt("stderr"): YMap({
        "target": YEnum(StdoutTargetType.entries()),
    }),

})


def _parse_config(data: str, schema: object, path: Optional[str] = None, ) -> Dict:
    try:
        doc = loadyaml(data, schema, label=path)
    except YAMLError as ex:
        raise ParseError(str(ex))

    return doc.data


def parse_task_config_str(data: str, path: Optional[str] = None, ) -> Dict:
    return _parse_config(data, _task_schema, path)


def parse_taskd_config_str(data: str, path: Optional[str] = None, ) -> Dict:
    return _parse_config(data, _taskd_schema, path)


def _read_file(filename: str):
    with open(filename, "rt", encoding='utf-8') as stream:
        return stream.read()


def parse_config_files(config_dir: str) -> (Dict, Dict[str, Dict]):
    taskd_path = os.path.join(config_dir, 'taskd.yaml')
    taskd_config_str = _read_file(taskd_path)
    taskd_config = parse_taskd_config_str(taskd_config_str, taskd_path)

    task_configs = {}
    configd_path = os.path.join(config_dir, 'config.d')
    for entry in os.scandir(configd_path):
        task, ext = os.path.splitext(entry.name)
        if ext.lower() != '.yaml':
            continue
        task_config_str = _read_file(entry.path)
        task_config = parse_task_config_str(task_config_str, entry.path)
        task_configs[task] = task_config

    return taskd_config, task_configs
