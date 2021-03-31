import asyncio
from asyncio import Task, Future
from logging import Logger
from typing import Optional, Tuple, Union, Awaitable, Callable, List

from expool import ExecutionPoolOpen
from expool.execution_pool_wrap import ExecutionPoolWrap


class ExecutionPoolMonitored(ExecutionPoolWrap):
    """
    ExecutionPoolOpen logging its jobs every N seconds.
    """

    def __init__(self, pool: ExecutionPoolOpen, logger: Logger, period=20):
        self._pool: ExecutionPoolOpen = pool
        self._period: int = period
        self._monitoring_task: Optional[Task] = None
        self._logger: Logger = logger
        super(ExecutionPoolMonitored, self).__init__(pool)

    async def add(self, job: Callable[[], Awaitable[None]]):
        self.start_monitoring()
        return await self._pool.add(job)

    async def close(self, timeout: Optional[Union[float, int]] = None):
        await self._pool.close(timeout)
        if self._monitoring_task is not None:
            self._monitoring_task.cancel()
            self._monitoring_task = None

    def start_monitoring(self):
        if self._monitoring_task is None:
            self._monitoring_task = asyncio.ensure_future(self._monitor())

    async def _monitor(self):
        while True:
            futures: Tuple[Future, ...] = self._pool.futures()
            active: List[Future] = [f for f in futures if not f.done()]
            self._logger.info(
                "%s active tasks count: %s. Tasks: %s",
                (
                    type(self).__name__,
                    len(active),
                    active,
                ),
            )
            self._logger.debug(
                "%s all tasks count (including tasks waiting to be flushed): %s. All tasks: %s",
                (
                    type(self).__name__,
                    len(futures),
                    futures,
                ),
            )
            try:
                await asyncio.sleep(self._period)
            except asyncio.CancelledError:
                return
