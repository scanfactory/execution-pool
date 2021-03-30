from typing import Callable, Awaitable

from expool.execution_pool_open import ExecutionPoolOpen
from expool.execution_pool_wrap import ExecutionPoolWrap


class CapReached(Exception):
    pass


class ExecutionPoolCapped(ExecutionPoolWrap):
    """
    ExecutionPoolOpen with a limited amount of jobs to be executed throughout its lifetime.

    Raises CapReached exception when reaches its limit.
    """

    def __init__(self, pool: ExecutionPoolOpen, max_jobs: int):
        self._pool: ExecutionPoolOpen = pool
        self._max_jobs: int = max_jobs
        self._jobs_count: int = 0
        super(ExecutionPoolCapped, self).__init__(pool)

    async def add(self, job: Callable[[], Awaitable[None]]):
        if self._jobs_count < self._max_jobs:
            await self._pool.add(job)
            self._jobs_count += 1
        else:
            raise CapReached
