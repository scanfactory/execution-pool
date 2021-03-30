from asyncio.futures import Future
from typing import Optional, Union, Callable, Awaitable, Tuple

from expool import ExecutionPoolOpen


class ExecutionPoolWrap(ExecutionPoolOpen):
    def __init__(self, pool: ExecutionPoolOpen):
        self.__pool: ExecutionPoolOpen = pool

    def futures(self) -> Tuple[Future, ...]:
        return self.__pool.futures()

    async def add(self, job: Callable[[], Awaitable[None]]):
        return await self.__pool.add(job)

    async def close(self, timeout: Optional[Union[float, int]] = None):
        return await self.__pool.close(timeout)
