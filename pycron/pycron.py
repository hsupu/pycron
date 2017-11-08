import logging
import datetime
import asyncio
import asyncio.subprocess

from typing import Optional, Mapping, Dict
from asyncio import AbstractEventLoop

from .run_id_generator import RunIdGeneratorType, RunIdGenerator, MemoryRunIdGenerator, FileRunIdGenerator
from .task import Task
from .watcher import Watcher


logger = logging.getLogger(__package__ + '.pycron')

WAKEUP_INTERVAL = datetime.timedelta(minutes=1)


def get_now() -> datetime.datetime:
    return datetime.datetime.utcnow()  # pragma: no cover


run_id_generator_map = {
    RunIdGeneratorType.MEMORY: MemoryRunIdGenerator,
    RunIdGeneratorType.FILE: FileRunIdGenerator,
}


class Pycron(object):
    def __init__(self, loop: AbstractEventLoop, global_config: Mapping, task_configs: Mapping[str, Mapping]) -> None:
        tasks = []
        for task_name in task_configs:
            task_config = task_configs[task_name]
            task = Task(task_name, task_config)
            tasks.append(task)
        self.tasks = tasks

        run_id_generator_config = global_config['runIdGenerator']
        run_id_generator_class = run_id_generator_map[run_id_generator_config['type']]
        self.run_id_generator = None if run_id_generator_class is None \
            else run_id_generator_class(run_id_generator_config)  # type: Optional[RunIdGenerator]

        self.loop = loop
        self._stop_event = asyncio.Event(loop=loop)
        self._actives = {}  # type: Dict[str, Watcher]

    async def run(self) -> None:
        while not self._stop_event.is_set():
            await self._spawn_tasks()
            try:
                await asyncio.wait_for(self._stop_event.wait(), 1, loop=self.loop)
            except asyncio.TimeoutError:
                pass

        self.run_id_generator.close()

        logger.info("waiting for running jobs..")
        await self._cancel_actives()

    def stop(self) -> None:
        self._stop_event.set()

    async def _spawn_tasks(self) -> None:
        now = get_now()
        for task in self.tasks:
            logger.info("next time ", task.cron.next())
            if task.cron.test(now):
                logger.info("starting %s (%s) at %d", task.name, task.cron_str, now.timestamp())
                await self._execute_task(task)

    async def _execute_task(self, task: Task) -> None:
        run_id = self.run_id_generator.generate()
        watcher = Watcher(self.loop, run_id, task, self._remove_from_actives)
        watcher.start()
        self._actives[run_id] = watcher

    def _remove_from_actives(self, run_id: str) -> None:
        self._actives.pop(run_id)

    async def _cancel_actives(self) -> None:
        pass
