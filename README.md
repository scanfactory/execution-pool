# Expool
[![EO principles respected here](https://www.elegantobjects.org/badge.svg)](https://www.elegantobjects.org)
[![Build Status](https://travis-ci.com/scanfactory/execution-pool.svg?branch=master)](https://travis-ci.com/scanfactory/execution-pool)
[![codecov](https://codecov.io/gh/scanfactory/execution-pool/branch/master/graph/badge.svg)](https://app.codecov.io/gh/scanfactory/execution-pool)

Simple asynchronous execution pool primitive.
You can think of it as of a `threading.ThreadPool` for coroutines.

## Usage
```python
import asyncio
from expool import ExecutionPoolSimple

async def main():
    pool = ExecutionPoolSimple(size=3) # size parameter sets the max amount of concurrent coroutines 
    
    async def some_job():
        await asyncio.sleep(3)
    
    await pool.add(some_job) # Returns immediately if the pool is not full.
    await pool.add(some_job) # If the pool max size is reached, waits 
    # until one of the pool's coroutines finishes.
    
    await pool.close()  # wait for all of the jobs to finish.
```

You may also set a timeout for `.close()` method:
```python
    await pool.close(timeout=10)  
```
If the timeout is reached, `ExecutionPoolSimple` cancels all remaining coroutines and returns.

You may also want to check out `ExecutionPool` decorators:
- `ExecutionPoolMonitored` - a pool with periodical logging of the jobs inside the pool;
- `ExecutionPoolCapped` - a pool with a limited lifespan.

## Installation
```shell
pip install expool
```

