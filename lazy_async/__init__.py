import asyncio
import concurrent.futures
from functools import wraps

__ALL__ = ['lazy', 'lazy_property']


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


class lazy_property:
    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        if doc is None and fget is not None:
            doc = fget.__doc__
        self.__doc__ = doc
        self.__name__ = fget.__name__

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if self.fget is None:
            raise AttributeError("unreadable attribute")

        is_async = asyncio.iscoroutinefunction(self.fget)
        cached_name = '__cached__' + self.__name__
        if cached_name in obj.__dict__:
            if is_async:
                return obj.__dict__[cached_name]
            else:
                return obj.__dict__[cached_name].result()
        else:
            if is_async:
                obj.__dict__[cached_name] = asyncio.Future()
            else:
                obj.__dict__[cached_name] = concurrent.futures.Future()

        if is_async:
            async def foo():
                obj.__dict__[cached_name] = asyncio.Future()
                try:
                    res = await self.fget(obj)
                except Exception as e:
                    obj.__dict__[cached_name].set_exception(e)
                    raise e

                obj.__dict__[cached_name].set_result(res)
                return res

            return foo()
        else:
            try:
                res = self.fget(obj)
            except Exception as e:
                obj.__dict__[cached_name].set_exception(e)
                raise e

            obj.__dict__[cached_name].set_result(res)
            return res

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")

        cached_name = '__cached__' + self.__name__
        if cached_name in obj.__dict__:
            del obj.__dict__[cached_name]
        self.fset(obj, value)

    def __delete__(self, obj):
        if self.fdel is None:
            raise AttributeError("can't delete attribute")

        cached_name = '__cached__' + self.__name__
        if cached_name in obj.__dict__:
            del obj.__dict__[cached_name]
        self.fdel(obj)

    def getter(self, fget):
        return type(self)(fget, self.fset, self.fdel, self.__doc__)

    def setter(self, fset):
        return type(self)(self.fget, fset, self.fdel, self.__doc__)

    def deleter(self, fdel):
        return type(self)(self.fget, self.fset, fdel, self.__doc__)
