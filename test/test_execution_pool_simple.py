import asyncio

import pytest

from expool import ExecutionPoolSimple, ExecutionPool, ExecutionPoolOpen
from test.helpers import (
    assert_all_jobs_done,
    assert_all_jobs_not_done,
    lock_all,
    unlock_all,
    OneTimeJob,
)


@pytest.mark.asyncio
@pytest.mark.parametrize("pool_size", [3, 2, 1])
async def test_simple_pool(pool_size):
    pool: ExecutionPool = ExecutionPoolSimple(size=pool_size)
    jobs = [OneTimeJob() for _ in range(pool_size + 1)]
    await lock_all(jobs)
    for job in jobs[:-1]:
        await asyncio.wait_for(
            pool.add(job),
            timeout=0.1,
        )
    last_job = jobs[-1]
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(pool.add(last_job), timeout=3)
    jobs[0].unlock()
    await asyncio.wait_for(
        pool.add(last_job),
        timeout=0.1,
    )
    assert jobs[0].done
    assert_all_jobs_not_done(jobs[1:])
    unlock_all(jobs[1:])

    await asyncio.sleep(0.2)
    assert_all_jobs_done(jobs)


@pytest.mark.asyncio
async def test_simple_pool_closing_timeout():
    pool = ExecutionPoolSimple(size=1)
    await pool.add(OneTimeJob(sleep_time=10))
    await pool.close(timeout=1)
    await asyncio.sleep(0.1)
    assert pool.futures()[0].cancelled()


@pytest.mark.asyncio
async def test_simple_pool_closing():
    pool = ExecutionPoolSimple(size=20)
    jobs = [OneTimeJob(sleep_time=0.2) for _ in range(20)]
    for job in jobs:
        await pool.add(job)
    await pool.close(timeout=0.5)
    assert_all_jobs_done(jobs)


@pytest.mark.asyncio
@pytest.mark.parametrize("pool_size", [0, -1])
async def test_simple_pool_bad_size(pool_size):
    with pytest.raises(ValueError):
        ExecutionPoolSimple(pool_size)


@pytest.mark.asyncio
async def test_simple_pool_futures():
    pool_size = 3
    pool: ExecutionPoolOpen = ExecutionPoolSimple(size=pool_size)
    jobs = [OneTimeJob() for _ in range(pool_size + 1)]
    await lock_all(jobs)
    for job in jobs[:-1]:
        await asyncio.wait_for(
            pool.add(job),
            timeout=0.1,
        )
    futures = pool.futures()
    assert len(futures) == pool_size
    jobs[0].unlock()
    await asyncio.wait_for(
        pool.add(jobs[-1]),
        timeout=0.1,
    )
    assert len(pool.futures()) == pool_size
    assert len(set(futures).union(pool.futures())) == pool_size + 1
    unlock_all(jobs[1:])
    await pool.close()
