import asyncio
import concurrent.futures
from functools import wraps

__ALL__ = ['lazy', 'lazy_getter']


class lazy:
    def __init__(self, func):
        self.__func = func
        wraps(self.__func)(self)
        self.is_async = asyncio.iscoroutinefunction(func)

    def __get__(self, inst, inst_cls):
        if inst is None:
            return self

        if not hasattr(inst, '__dict__'):
            raise AttributeError("'%s' object has no attribute '__dict__'" % (inst_cls.__name__,))

        cached_name = '__cached__' + self.__name__
        if cached_name in inst.__dict__:
            if self.is_async:
                async def foo():
                    return await inst.__dict__[cached_name]

                return foo
            else:
                return lambda: inst.__dict__[cached_name].result()
        else:
            if self.is_async:
                inst.__dict__[cached_name] = asyncio.Future()
            else:
                inst.__dict__[cached_name] = concurrent.futures.Future()

        if self.is_async:
            async def foo():
                inst.__dict__[cached_name] = asyncio.Future()
                try:
                    res = await self.__func(inst)
                except Exception as e:
                    inst.__dict__[cached_name].set_exception(e)
                    raise e

                inst.__dict__[cached_name].set_result(res)
                return res

            return foo
        else:
            try:
                res = self.__func(inst)
            except Exception as e:
                inst.__dict__[cached_name].set_exception(e)
                raise e

            inst.__dict__[cached_name].set_result(res)
            return lambda: res


class lazy_getter:
    def __init__(self, func):
        self.__func = func
        wraps(self.__func)(self)
        self.is_async = asyncio.iscoroutinefunction(func)

    def __get__(self, inst, inst_cls):
        if inst is None:
            return self

        if not hasattr(inst, '__dict__'):
            raise AttributeError("'%s' object has no attribute '__dict__'" % (inst_cls.__name__,))

        cached_name = '__cached__' + self.__name__
        if cached_name in inst.__dict__:
            if self.is_async:
                return inst.__dict__[cached_name]
            else:
                return inst.__dict__[cached_name].result()
        else:
            if self.is_async:
                inst.__dict__[cached_name] = asyncio.Future()
            else:
                inst.__dict__[cached_name] = concurrent.futures.Future()

        if self.is_async:
            async def foo():
                inst.__dict__[cached_name] = asyncio.Future()
                try:
                    res = await self.__func(inst)
                except Exception as e:
                    inst.__dict__[cached_name].set_exception(e)
                    raise e

                inst.__dict__[cached_name].set_result(res)
                return res

            return foo()
        else:
            try:
                res = self.__func(inst)
            except Exception as e:
                inst.__dict__[cached_name].set_exception(e)
                raise e

            inst.__dict__[cached_name].set_result(res)
            return res
