""" 内置缓存模块使用示例

最近最少使用（Least Recently Used, LRU）缓存机制
"""

import time
from functools import lru_cache

times = 35


@lru_cache(times)
def fibonacci(n):
    return n if n < 2 else fibonacci(n - 1) + fibonacci(n - 2)


def fibonacci_no_cache(n):
    return n if n < 2 else fibonacci_no_cache(n - 1) + fibonacci_no_cache(n - 2)


start_time = time.time()
for i in range(times):
    fibonacci(i)
print(round(time.time() - start_time, 2))

start_time = time.time()
for i in range(times):
    fibonacci_no_cache(i)
print(round(time.time() - start_time, 2))
