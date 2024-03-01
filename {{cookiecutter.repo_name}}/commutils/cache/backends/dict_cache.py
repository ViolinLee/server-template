""" 借助内置字典类型实现的缓存类
"""

import time
from .base import BaseCache
from collections import defaultdict


class DictCache(BaseCache):
    """ 字典缓存类

    内存清理存在滞后性：缓存到期不会主动从缓存中移除键值，会在下一次调用get方法时移除
    """

    def __init__(self, dexp=3153600000):
        super(DictCache, self).__init__(dexp)

        self._cache = defaultdict(lambda: (None, None))

    @property
    def cache(self):
        return dict(self._cache)

    def set(self, key, value, expire=None):
        expire_sec = expire if expire is not None else self._config["dexp"]
        self._cache[key] = (value, None if expire_sec is None else time.time() + expire_sec)

    def set_many(self, values, expire=None, keep_type=True):
        assert keep_type == True, "不支持keep_type=False"
        [self.set(key, value, expire) for key, value in values.items()]
        return []

    def get(self, key):
        """ 从缓存取值

        :param key:
        :return: 过期
        """
        if key not in self._cache.keys():
            # 键不存在时直接返回,防止索引操作将不存在的键写入缓存造成空间浪费
            return None

        (val, expire_ts) = self._cache[key]
        if expire_ts is not None and time.time() > expire_ts and key in self._cache.keys():
            self.delete(key)
            return None
        else:
            return val

    def get_many(self, keys):
        if not keys:
            return {}
        else:
            return {key: self.get(key) for key in keys}

    def replace(self, key, value, expire=None) -> bool:
        if key in self._cache.keys():
            self.set(key, value, expire)
        else:
            raise KeyError

        return True

    def delete(self, *keys):
        for key in keys:
            del (self._cache[key])

        return True

    def flush_all(self):
        self._cache.clear()

        return True

