""" 缓存装饰器测试用例

"""

import time
import json

# 直接运行的脚本,使用绝对路径导入
from commutils.cache import easycache
from commutils.cache.backends import RedisCache, DictCache
from commutils.db import RedisPool


last_time = None

redis_pool = RedisPool.from_url("redis://localhost:6379/1", decode_responses=True)
redis_cache = RedisCache(redis_pool)


def basic_test(cache):
    # set
    cache.set('YZ', 'yz')
    print(cache.cache)
    cache.set_many({'GOOGLE': 'google', 'APPLE': 'apple'})
    print(cache.cache)
    print(cache.get_many(['GOOGLE', 'APPLE', 'NONE']))

    # expiry
    cache.set('DJI', 'dji', 2)
    print(cache.cache)
    print(cache.get('DJI'))
    time.sleep(2)
    print(cache.get('DJI'))
    print(cache.cache)

    cache.delete('GOOGLE')
    print(cache.cache)

    cache.flush_all()
    print(cache.cache)


# 不传backend则使用字典缓存;缓存2秒(去掉dexp则会永久缓存)
@easycache(backend=redis_cache, cache_key='cur_time', dexp=2)
def cur_time():
    global last_time

    cur_time = time.time()
    if last_time is None:
        last_time = cur_time

    if cur_time - last_time > 5:
        last_time = cur_time

    # 注意:若使用redis缓存,特殊数据类型需转为json字符串,此处存储tuple再取出时为list类型
    return json.dumps((cur_time,))


if __name__ == '__main__':
    CACHE_TYPE = "redis"

    # 缓存类测试
    if CACHE_TYPE == "dict":
        cache = DictCache()
    elif CACHE_TYPE == "redis":
        cache = redis_cache
    else:
        cache = None
    basic_test(cache)

    # 装饰器测试
    print(f"Initial call: {cur_time()}")
    time.sleep(1)
    print(f"In caching lifecycle call: {cur_time()}")
    time.sleep(2)
    print(f"Initial call in a new lifecycle: {cur_time()}")
    time.sleep(1)
    print(f"In caching lifecycle call: {cur_time()}")
