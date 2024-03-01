""" 借助redis实现的缓存类
"""

import threading
from typing import Union

from .base import BaseCache
from commutils.db.redis_conn import RedisPool


class RedisCache(BaseCache):

    def __init__(self, pool: RedisPool, dexp=None):
        super(RedisCache, self).__init__(dexp)

        self._cache = pool
        self._local_keys = []
        self._lock = threading.Lock()

    @property
    def cache(self):
        return self.get_many(self._local_keys)

    def set(self, key, value, expire=None):
        self._cache.set(key, value, expire if expire is not None else self._config["dexp"])
        self._push_key(key) if key not in self._local_keys else None

    def set_many(self, values, expire=None, keep_type=True):
        """
        原子性操作以确保_local_keys变量维护的键是正确的
        :param values:
        :param expire:
        :param keep_type:
        :return:
        """
        with self._cache.pipeline() as pipe:
            if expire is None and self._config["dexp"] is None:
                if keep_type:
                    [pipe.set(key, value) for key, value in values.items()]
                else:
                    pipe.mset(values)
            else:
                expire_sec = expire if expire is not None else self._config["dexp"]
                for key, value in values.items():
                    pipe.set(key, value)
                    pipe.expire(key, expire_sec)

            pipe.execute()

        self._push_key([key for key in values.keys() if key not in self._local_keys])

    def get(self, key):
        return self._cache.get(key)

    def get_many(self, keys):
        values = self._cache.mget(keys)
        return {key: values[i] for i, key in enumerate(keys)}

    def replace(self, key, value, expire):
        if key in self._local_keys:
            self._cache.set(key, value, expire)
        else:
            raise KeyError

        return True

    def delete(self, *keys):
        self._cache.delete(*keys)

        for key in keys:
            self._local_keys.remove(key) if key in self._local_keys else None

        return True

    def flush_all(self):
        self.delete(*self._local_keys)

    def _push_key(self, keys: Union[str, list]):
        with self._lock:
            self._local_keys.extend(keys) if isinstance(keys, list) else self._local_keys.append(keys)
