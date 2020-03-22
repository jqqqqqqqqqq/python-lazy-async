# Lazy Evaluation

Lazy evaluate function/class method/class property getter. The target will be evaluated once and only once on first call
, and concurrent calls will get the result immediately once the target is ready and gets the same exception when the target
raises some exception.

Compatible with both sync and async.

## Example

```python
from lazy_async import lazy, lazy_getter
import asyncio
import time

class ExampleClass:
    def __init__(self):
        self.sync_called = 0
        self.async_called = 0

    @lazy
    def func1(self):
        time.sleep(5)
        self.sync_called += 1
        return 'something'

    @lazy
    async def func2(self):
        await asyncio.sleep(5)
        self.async_called += 1
        return 'something'

    @lazy
    def func3(self):
        time.sleep(5)
        raise ValueError('SomeException')

    @lazy
    async def func4(self):
        await asyncio.sleep(5)
        raise ValueError('SomeException')

    @lazy_getter
    def func5(self):
        time.sleep(5)
        return 'something'

    @lazy_getter
    async def func6(self):
        await asyncio.sleep(5)
        return 'something'
```

See unittest for detailed example.