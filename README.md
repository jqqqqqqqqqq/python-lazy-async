# Lazy Evaluation
![build](https://travis-ci.org/jqqqqqqqqqq/python-lazy-async.svg?branch=master)
![shields](https://img.shields.io/badge/python-3.7%2B-blue.svg?style=flat-square)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

Lazy evaluate function/class method/class property. The target will be evaluated once and only once on first call
, and concurrent calls will get the result immediately once the target is ready and gets the same exception when the target
raises some exception.

## Features

- Compatible with both sync and async

- Lock free!!!! (thanks to asyncio.Future and concurrent.futures.Future, all the operations are atomic)

- Async property must use sync setter and deleter for now, due to the limitation that python does not support await
before assignment or `del`. `await setattr(foo, value)` is one possible workaround, but it introduces more obfuscation.

## Installation

```bash
pip install lazy-async
```

## Example

```python
import asyncio
from lazy_async import lazy, lazy_property, lazy_async, lazy_property_async
from threading import Thread
import time


class ExampleClass:
    def __init__(self):
        self.sync_called = 0
        self.async_called = 0
        self.prop = 'nothing'

    @lazy
    def func1(self):
        time.sleep(5)
        self.sync_called += 1
        return 'something'

    @lazy_async
    async def func2(self):
        await asyncio.sleep(5)
        self.async_called += 1
        return 'something'

    @lazy
    def func3(self):
        time.sleep(5)
        raise ValueError('SomeException')

    @lazy_async
    async def func4(self):
        await asyncio.sleep(5)
        raise ValueError('SomeException')

    @lazy_property
    def func5(self):
        time.sleep(5)
        self.sync_called += 1
        return self.prop

    @func5.setter
    def func5(self, value):
        self.prop = value

    @lazy_property_async
    async def func6(self):
        await asyncio.sleep(5)
        self.async_called += 1
        return self.prop

    @func6.setter
    def func6(self, value):
        self.prop = value

def test_something_sync():
    test_class = ExampleClass()
    test1 = dict()

    def start1():
        test1[1] = test_class.func1()

    def start2():
        time.sleep(3)
        test1[2] = test_class.func1()

    def start3():
        time.sleep(10)
        test1[3] = test_class.func1()

    Thread(target=start1).start()
    Thread(target=start2).start()
    Thread(target=start3).start()
    time.sleep(1)
    assert test1 == {}
    time.sleep(3)
    assert test1 == {}
    time.sleep(2)
    assert test1 == {1: 'something', 2: 'something'}
    time.sleep(5)
    assert test1 == {1: 'something', 2: 'something', 3: 'something'}


def test_something_async():
    test2 = dict()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    test_class = ExampleClass()

    async def start1():
        test2[1] = await test_class.func2()

    async def start2():
        await asyncio.sleep(3)
        test2[2] = await test_class.func2()

    async def start3():
        await asyncio.sleep(10)
        test2[3] = await test_class.func2()

    async def assert1():
        await asyncio.sleep(1)
        assert test2 == {}
        await asyncio.sleep(3)
        assert test2 == {}
        await asyncio.sleep(2)
        assert test2 == {1: 'something', 2: 'something'}
        await asyncio.sleep(5)
        assert test2 == {1: 'something', 2: 'something', 3: 'something'}

    loop.run_until_complete(asyncio.gather(start1(), start2(), start3(), assert1()))
```

See unittest for more examples.
