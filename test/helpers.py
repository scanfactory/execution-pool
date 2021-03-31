import asyncio


def assert_all_jobs_done(jobs):
    for job in jobs:
        assert job.done


def assert_all_jobs_not_done(jobs):
    for job in jobs:
        assert not job.done


async def lock_all(jobs):
    for job in jobs:
        await job.lock()


def unlock_all(jobs):
    for job in jobs:
        job.unlock()


class OneTimeJob:
    def __init__(self, sleep_time: float = 0.01):
        self._lock: asyncio.Lock = asyncio.Lock()
        self.done: bool = False
        self._sleep_time: float = sleep_time

    async def __call__(self) -> None:
        if self.done:
            raise TypeError("Already called! (Should not be raised)")
        async with self._lock:
            await asyncio.sleep(self._sleep_time)
            self.done = True

    async def lock(self):
        await self._lock.acquire()

    def unlock(self):
        self._lock.release()


try:
    from unittest.mock import seal  # type: ignore
except ImportError:

    def seal(mock) -> None:
        pass
