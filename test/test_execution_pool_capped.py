import pytest

from expool import ExecutionPoolCapped, ExecutionPoolSimple
from expool.execution_pool_capped import CapReached
from test.helpers import OneTimeJob


@pytest.mark.asyncio
async def test_execution_pool_capped():
    pool = ExecutionPoolCapped(ExecutionPoolSimple(size=1), max_jobs=3)
    await pool.add(OneTimeJob())
    await pool.add(OneTimeJob())
    await pool.add(OneTimeJob())
    with pytest.raises(CapReached):
        await pool.add(OneTimeJob())
    await pool.close()
