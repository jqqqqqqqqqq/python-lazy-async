import pytest
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
    assert test_class.sync_called == 1


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
        assert test_class.async_called == 1

    loop.run_until_complete(asyncio.gather(start1(), start2(), start3(), assert1()))


def test_exception_sync():
    test_class = ExampleClass()

    def start1():
        try:
            test_class.func3()
        except Exception as e:
            assert isinstance(e, ValueError)

    def start2():
        time.sleep(3)
        try:
            test_class.func3()
        except Exception as e:
            assert isinstance(e, ValueError)

    def start3():
        time.sleep(10)
        try:
            test_class.func3()
        except Exception as e:
            assert isinstance(e, ValueError)

    Thread(target=start1).start()
    Thread(target=start2).start()
    Thread(target=start3).start()
    time.sleep(11)


def test_exception_async():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    test_class = ExampleClass()
    exception_count = 0

    async def start1():
        try:
            await test_class.func4()
        except Exception as e:
            nonlocal exception_count
            exception_count += 1
            assert isinstance(e, ValueError)

    async def start2():
        await asyncio.sleep(3)
        try:
            await test_class.func4()
        except Exception as e:
            nonlocal exception_count
            exception_count += 1
            assert isinstance(e, ValueError)

    async def start3():
        await asyncio.sleep(10)
        try:
            await test_class.func4()
        except Exception as e:
            nonlocal exception_count
            exception_count += 1
            assert isinstance(e, ValueError)

    loop.run_until_complete(asyncio.gather(start1(), start2(), start3()))
    assert exception_count == 3


def test_something_property_sync():
    test_class = ExampleClass()
    test5 = dict()

    def start1():
        test5[1] = test_class.func5

    def start2():
        time.sleep(3)
        test5[2] = test_class.func5

    def start3():
        time.sleep(7)
        test5[3] = test_class.func5

    def start4():
        time.sleep(9)
        test_class.func5 = 'something'
        test5[4] = test_class.func5

    def start5():
        time.sleep(12)
        test5[5] = test_class.func5

    Thread(target=start1).start()
    Thread(target=start2).start()
    Thread(target=start3).start()
    Thread(target=start4).start()
    Thread(target=start5).start()
    time.sleep(1)
    assert test5 == {}
    time.sleep(3)
    assert test5 == {}
    time.sleep(2)
    assert test5 == {1: 'nothing', 2: 'nothing'}
    time.sleep(3)
    assert test5 == {1: 'nothing', 2: 'nothing', 3: 'nothing'}
    assert test_class.sync_called == 1
    time.sleep(2)
    assert test5 == {1: 'nothing', 2: 'nothing', 3: 'nothing'}
    time.sleep(5)
    assert test5 == {1: 'nothing', 2: 'nothing', 3: 'nothing', 4: 'something', 5: 'something'}
    assert test_class.sync_called == 2


def test_something_property_async():
    test6 = dict()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    test_class = ExampleClass()

    async def start1():
        test6[1] = await test_class.func6

    async def start2():
        await asyncio.sleep(3)
        test6[2] = await test_class.func6

    async def start3():
        await asyncio.sleep(7)
        test6[3] = await test_class.func6

    async def start4():
        await asyncio.sleep(9)
        test_class.func6 = 'something'
        test6[4] = await test_class.func6

    async def start5():
        await asyncio.sleep(12)
        test6[5] = await test_class.func6

    async def assert1():
        await asyncio.sleep(1)
        assert test6 == {}
        await asyncio.sleep(3)
        assert test6 == {}
        await asyncio.sleep(2)
        assert test6 == {1: 'nothing', 2: 'nothing'}
        await asyncio.sleep(3)
        assert test6 == {1: 'nothing', 2: 'nothing', 3: 'nothing'}
        assert test_class.async_called == 1
        await asyncio.sleep(2)
        assert test6 == {1: 'nothing', 2: 'nothing', 3: 'nothing'}
        await asyncio.sleep(5)
        assert test6 == {1: 'nothing', 2: 'nothing', 3: 'nothing', 4: 'something', 5: 'something'}
        assert test_class.async_called == 2

    loop.run_until_complete(asyncio.gather(start1(), start2(), start3(), start4(), start5(), assert1()))


def test_something_sync_crazy():
    test_class = ExampleClass()

    def start():
        assert test_class.func1() == 'something'

    [Thread(target=start).start() for _ in range(2000)]
    time.sleep(6)
    assert test_class.sync_called == 1


def test_something_async_crazy():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    test_class = ExampleClass()

    async def start():
        assert await test_class.func2() == 'something'

    loop.run_until_complete(asyncio.gather(*[start() for _ in range(2000)]))

    assert test_class.async_called == 1


def test_something_property_sync_crazy():
    test_class = ExampleClass()
    count = 0

    def start():
        nonlocal count
        assert test_class.func5 == 'nothing'
        count += 1

    [Thread(target=start).start() for _ in range(2000)]
    time.sleep(15)  # safe value due to performance issue
    assert count == 2000
    assert test_class.sync_called == 1

    test_class.func5 = 'something'
    count = 0

    def start2():
        nonlocal count
        assert test_class.func5 == 'something'
        count += 1

    [Thread(target=start2).start() for _ in range(2000)]
    time.sleep(15)  # safe value due to performance issue
    assert count == 2000
    assert test_class.sync_called == 2


def test_something_property_async_crazy():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    test_class = ExampleClass()

    async def start():
        assert await test_class.func6 == 'nothing'

    loop.run_until_complete(asyncio.gather(*[start() for _ in range(2000)]))

    assert test_class.async_called == 1

    test_class.func6 = 'something'

    async def start2():
        assert await test_class.func6 == 'something'

    loop.run_until_complete(asyncio.gather(*[start2() for _ in range(2000)]))

    assert test_class.async_called == 2
