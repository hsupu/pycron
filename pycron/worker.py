import logging
import os
import asyncio

from typing import Optional
from asyncio import StreamReader, StreamWriter
from asyncio.subprocess import Process

from .pycron import Task


logger = logging.getLogger(__package__ + '.worker')

CHUNK_SIZE = 4096


async def _read_fd_write_stream(loop: asyncio.AbstractEventLoop, rfd: int, writer: StreamWriter) -> None:
    f = os.fdopen(rfd, mode="rb")
    try:
        while True:
            b = await loop.run_in_executor(None, f.read, CHUNK_SIZE)
            if not b:
                break
            writer.write(b)
        writer.write_eof()
        await writer.drain()
    finally:
        f.close()


async def _read_stream_write_fd(loop: asyncio.AbstractEventLoop, reader: StreamReader, wfd: int) -> None:
    f = os.fdopen(wfd, mode="wb")
    try:
        while True:
            b = await reader.read(CHUNK_SIZE)
            if not b:
                break
            await loop.run_in_executor(None, f.write, b)
    finally:
        f.close()


class Worker:
    def __init__(self, loop: asyncio.AbstractEventLoop, run_id: str, task: Task):
        self.loop = loop
        self.run_id = run_id
        self.task = task
        self.process = None  # type: Optional[Process]
        self.exit_code = None  # type: Optional[int]
        self._stdin_task = None  # type: Optional[asyncio.Task]
        self._stdout_task = None  # type: Optional[asyncio.Task]
        self._stderr_task = None  # type: Optional[asyncio.Task]

    async def start(self) -> None:
        """
        execute subprocess by task config
        :return:
        """
        program = self.task.executable

        args = [program]
        args.extend(self.task.args)

        kwargs = {}

        env = self.task.env.copy()
        env.update(os.environ.items())
        kwargs['env'] = env

        if self.task.stdin is not None:
            kwargs['stdin'] = asyncio.subprocess.PIPE
        if self.task.stdout is not None:
            kwargs['stdout'] = asyncio.subprocess.PIPE
        if self.task.stderr is not None:
            kwargs['stderr'] = asyncio.subprocess.PIPE

        self.process = await asyncio.create_subprocess_exec(*args, **kwargs, loop=self.loop)

        if self.task.stdin is not None:
            rfd = self.task.stdin.openfd()
            read_task = _read_fd_write_stream(self.loop, rfd, self.process.stdin)
            self._stdin_task = self.loop.create_task(read_task)
        if self.task.stdout is not None:
            wfd = self.task.stdout.openfd(self.run_id)
            write_task = _read_stream_write_fd(self.loop, self.process.stdout, wfd)
            self._stdout_task = self.loop.create_task(write_task)
        if self.task.stderr is not None:
            wfd = self.task.stderr.openfd(self.run_id)
            write_task = _read_stream_write_fd(self.loop, self.process.stderr, wfd)
            self._stderr_task = self.loop.create_task(write_task)

    async def wait(self, timeout=0) -> int:
        """
        waiting until subprocess exit or timeout
        :param timeout:
        :return: exit_code if exit normally, -1 if timeout
        """
        if self.process is None:
            raise RuntimeError("job is not started")
        if timeout > 0:
            try:
                self.exit_code = await asyncio.wait_for(self.process.wait(), timeout, loop=self.loop)
            except asyncio.TimeoutError:
                return -1
        else:
            self.exit_code = await self.process.wait()
        return self.exit_code

    async def exit(self, timeout=10) -> None:
        """
        signal subprocess: try SIGTERM first, send SIGKILL if timeout
        :param timeout:
        :return:
        """
        if self.process is None:
            raise RuntimeError("job is not started")
        self.process.terminate()
        try:
            await asyncio.wait_for(self.process.wait(), timeout, loop=self.loop)
        except asyncio.TimeoutError:
            logger.warning("job cannot exit gracefully, killing it..")
            self.process.kill()
