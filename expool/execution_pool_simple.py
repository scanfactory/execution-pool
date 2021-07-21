import asyncio
from asyncio import Future
from typing import Awaitable, Callable, Set, Tuple

from expool.execution_pool_open import ExecutionPoolOpen


class ExecutionPoolSimple(ExecutionPoolOpen):
    """
    ExecutionPoolOpen simple implementation.
    """

    def __init__(self, size: int):
        if size < 1:
            raise ValueError("Size must be >= 1. Got: %r" % size)
        self._size: int = size
        self._tasks: Set[Future] = set()

    async def add(self, job: Callable[[], Awaitable[None]]):
        if len(self._tasks) < self._size:
            self._add(job)
        else:
            done, pending = await asyncio.wait(
                self._tasks, return_when=asyncio.FIRST_COMPLETED
            )
            self._tasks = pending
            self._add(job)

    def _add(self, job: Callable[[], Awaitable[None]]):
        self._tasks.add(asyncio.ensure_future(job()))

    async def close(self, timeout=None):
        try:
            await asyncio.wait_for(
                asyncio.wait(
                    self._tasks,
                    return_when=asyncio.ALL_COMPLETED,
                ),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            for t in self._tasks:
                t.cancel()

    def futures(self) -> Tuple[Future, ...]:
        return tuple(self._tasks)
