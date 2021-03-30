import asyncio
from unittest.mock import Mock, call

import pytest

from expool import ExecutionPoolSimple
from expool.execution_pool_monitored import ExecutionPoolMonitored
from test.helpers import (
    OneTimeJob,
    lock_all,
    assert_all_jobs_not_done,
    unlock_all,
    assert_all_jobs_done,
    seal,
)


@pytest.mark.asyncio
@pytest.mark.parametrize("pool_size", [3, 2, 1])
async def test_monitored_pool_basic_functionality(pool_size):
    logger = Mock(
        info=Mock(return_value=None),
        warning=Mock(return_value=None),
        exception=Mock(return_value=None),
    )
    seal(logger)
    pool = ExecutionPoolMonitored(
        ExecutionPoolSimple(size=pool_size), logger=logger, period=0.3
    )
    jobs = [OneTimeJob() for i in range(pool_size + 1)]
    await lock_all(jobs)

    for job in jobs[:pool_size]:
        await asyncio.wait_for(
            pool.add(job),
            timeout=0.1,
        )
    job = jobs[pool_size]
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(pool.add(job), timeout=3)
    jobs[0].unlock()
    await asyncio.wait_for(
        pool.add(job),
        timeout=0.1,
    )
    assert jobs[0].done
    assert_all_jobs_not_done(jobs[1:])
    unlock_all(jobs[1:])

    await asyncio.sleep(0.2)
    assert_all_jobs_done(jobs)
    await pool.close()


@pytest.mark.asyncio
async def test_monitored_pool_monitoring():
    logger = Mock(
        info=Mock(return_value=None),
        warning=Mock(return_value=None),
        exception=Mock(return_value=None),
    )
    pool = ExecutionPoolMonitored(
        ExecutionPoolSimple(size=3),
        logger=logger,
        period=0.5,
    )
    job = OneTimeJob(sleep_time=1)
    await pool.add(job)
    futures = list(pool.futures())
    assert len(futures) == 1
    await asyncio.sleep(1.9)
    await pool.close()
    assert logger.info.call_args_list == [
        call(
            "%s active tasks count: %s. Tasks: %s",
            ("ExecutionPoolMonitored", 1, futures),
        ),
        call(
            "%s active tasks count: %s. Tasks: %s",
            ("ExecutionPoolMonitored", 1, futures),
        ),
        call("%s active tasks count: %s. Tasks: %s", ("ExecutionPoolMonitored", 0, [])),
        call("%s active tasks count: %s. Tasks: %s", ("ExecutionPoolMonitored", 0, [])),
    ]
