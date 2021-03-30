from abc import ABC, abstractmethod
from typing import Callable, Awaitable, Optional, Union


class ExecutionPool(ABC):
    """
    Async jobs execution pool.
    """

    @abstractmethod
    async def add(self, job: Callable[[], Awaitable[None]]):
        """
        Add a job to be executed.
        If the pool is already full, block until one of the running jobs exits.
        """
        pass

    @abstractmethod
    async def close(self, timeout: Optional[Union[float, int]] = None):
        """
        Wait for the given amount of seconds until every running job exits.

        If timeout=None it's up to the ExecutionPool instance to decide how long to wait.
        """
        pass
