""" 缓存装饰器工厂类

"""

from functools import wraps
from .backends import BaseCache
from ..common import ignore_errors


cache_ignore_errors = True


class CacheDecoratorFactory:
    """ 缓存装饰器工厂类

    注意:会使用全局变量cache_ignore_errors
    """

    def __init__(self, backend, cache_key='', expire_key='', **kwargs):
        assert isinstance(backend, BaseCache)

        self._backend = backend
        self._backend.update_cfg(**kwargs)

        if cache_key:
            self.key = cache_key
            self._wrapped = self._caching_wrapper

        if expire_key:
            self.key = expire_key
            self._wrapped = self._expiry_wrapper

        global cache_ignore_errors
        cache_ignore_errors = kwargs.get('ignore_errors', False)

    def __call__(self, func):
        return self._wrapped(func)

    @ignore_errors(cache_ignore_errors)
    def _caching_wrapper(self, func):
        @wraps(func)
        def cache_setter(*args, **kwargs):
            key = self.key(*args, **kwargs) if callable(self.key) else self.key.format(*args, **kwargs)
            result = self._backend.get(key)

            if not result:
                result = func(*args, **kwargs)
                self._backend.set(key, result)

            return result
        return cache_setter

    @ignore_errors(cache_ignore_errors)
    def _expiry_wrapper(self, func):
        @wraps(func)
        def cache_deleter(*args, **kwargs):
            key = self.key(*args, **kwargs) if callable(self.key) else self.key.format(*args, **kwargs)
            self._backend.delete(key)

            return func(*args, **kwargs)
        return cache_deleter
