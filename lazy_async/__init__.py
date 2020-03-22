import asyncio
import concurrent.futures
from functools import wraps

__ALL__ = ['lazy', 'lazy_property', 'lazy_async', 'lazy_property_async']


class lazy:
    def __init__(self, func):
        self.fget = func
        wraps(self.fget)(self)

    def __get__(self, obj, objtype):
        if obj is None:
            return self

        if not hasattr(obj, '__dict__'):
            raise AttributeError("'%s' object has no attribute '__dict__'" % (objtype.__name__,))

        cached_name = '__cached__' + self.__name__
        cache = obj.__dict__.get(cached_name)  # get is atomic

        if cache:
            return lambda: cache.result()
        else:
            future = concurrent.futures.Future()
            obj.__dict__.setdefault(cached_name, future)  # atomic set
            cache = obj.__dict__.get(cached_name)
            if cache is not future:  # only one future is set, so only execute once is guaranteed
                return lambda: cache.result()

        try:
            res = self.fget(obj)
        except Exception as e:
            cache.set_exception(e)
            raise e

        cache.set_result(res)  # notify all futures
        return lambda: res


class lazy_async:
    def __init__(self, func):
        self.fget = func
        wraps(self.fget)(self)

    def __get__(self, obj, objtype):
        if obj is None:
            return self

        if not hasattr(obj, '__dict__'):
            raise AttributeError("'%s' object has no attribute '__dict__'" % (objtype.__name__,))

        cached_name = '__cached__' + self.__name__

        cache = obj.__dict__.get(cached_name)

        async def foo():
            return await cache

        if cache:
            return foo
        else:
            cache = asyncio.Future()
            obj.__dict__[cached_name] = cache

        async def bar():
            try:
                res = await self.fget(obj)
            except Exception as e:
                cache.set_exception(e)
                raise e

            cache.set_result(res)
            return res

        return bar


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

        cached_name = '__cached__' + self.__name__
        cache = obj.__dict__.get(cached_name)

        if cache:
            return cache.result()
        else:
            future = concurrent.futures.Future()
            obj.__dict__.setdefault(cached_name, future)
            cache = obj.__dict__.get(cached_name)
            if cache is not future:
                return cache.result()

        try:
            res = self.fget(obj)
        except Exception as e:
            cache.set_exception(e)
            raise e

        cache.set_result(res)
        return res

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")

        cached_name = '__cached__' + self.__name__
        cache = concurrent.futures.Future()
        obj.__dict__[cached_name] = cache
        cache.set_result(value)

        self.fset(obj, value)

    def __delete__(self, obj):
        if self.fdel is None:
            raise AttributeError("can't delete attribute")

        cached_name = '__cached__' + self.__name__
        obj.__dict__.pop(cached_name, None)

        self.fdel(obj)

    def getter(self, fget):
        return type(self)(fget, self.fset, self.fdel, self.__doc__)

    def setter(self, fset):
        return type(self)(self.fget, fset, self.fdel, self.__doc__)

    def deleter(self, fdel):
        return type(self)(self.fget, self.fset, fdel, self.__doc__)


class lazy_property_async:
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

        cached_name = '__cached__' + self.__name__
        cache = obj.__dict__.get(cached_name)

        async def foo():
            return await cache

        if cache:
            return foo()
        else:
            future = asyncio.Future()
            obj.__dict__.setdefault(cached_name, future)
            cache = obj.__dict__.get(cached_name)  # test
            if cache is not future:
                return foo()

        async def foo():
            try:
                res = await self.fget(obj)
            except Exception as e:
                cache.set_exception(e)
                raise e

            cache.set_result(res)
            return res

        return foo()

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")

        cached_name = '__cached__' + self.__name__
        cache = asyncio.Future()
        obj.__dict__[cached_name] = cache
        cache.set_result(value)

        self.fset(obj, value)

    def __delete__(self, obj):
        if self.fdel is None:
            raise AttributeError("can't delete attribute")

        cached_name = '__cached__' + self.__name__
        obj.__dict__.pop(cached_name, None)

        self.fdel(obj)

    def getter(self, fget):
        return type(self)(fget, self.fset, self.fdel, self.__doc__)

    def setter(self, fset):
        return type(self)(self.fget, fset, self.fdel, self.__doc__)

    def deleter(self, fdel):
        return type(self)(self.fget, self.fset, fdel, self.__doc__)