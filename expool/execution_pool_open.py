from abc import abstractmethod
from asyncio import Future
from typing import Tuple

from expool.execution_pool import ExecutionPool


class ExecutionPoolOpen(ExecutionPool):
    """
    An ExecutionPool providing a collection of the futures currently being awaited.
    """

    @abstractmethod
    def futures(self) -> Tuple[Future, ...]:
        """
        Returns a list of jobs currently being awaited
        """
        pass
