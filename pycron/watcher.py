import logging
import asyncio

from typing import Optional, Callable
from asyncio import AbstractEventLoop

from .task import Task
from .worker import Worker


logger = logging.getLogger(__package__ + '.watcher')


class Watcher(object):
    def __init__(self, loop: AbstractEventLoop, run_id: str, task: Task, done_callback: Callable[[str], None]) -> None:
        self.loop = loop
        self.run_id = run_id
        self.worker = Worker(loop, run_id, task)
        self._done_callback = done_callback
        self._done_event = None  # type: Optional[asyncio.Event]
        self._loop_task = None  # type: Optional[asyncio.Task]

    def start(self) -> None:
        self._done_event = asyncio.Event(loop=self.loop)
        self._loop_task = self.loop.create_task(self._run())

    async def _run(self) -> None:
        """
        report start, start, wait and report result
        :return:
        """
        try:
            await self.worker.start()
            exit_code = -1
            while exit_code == -1:
                exit_code = await self.worker.wait(timeout=1)
            self._done_event.set()
            self._done_callback(self.run_id)
            if exit_code & 128:
                logger.warning("run_%s killed by signal %d", self.run_id, exit_code & 127)
            else:
                logger.info("run_%s exited with code %d", self.run_id, exit_code)
        except Exception:
            logger.exception("bug!")

    def is_done(self) -> bool:
        return self._done_event.is_set()

    def cancel(self) -> None:
        self.worker.exit(timeout=5)
