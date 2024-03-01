import warnings
from .dict_cache import BaseCache, DictCache

try:
    from .redis_cache import RedisCache
except ImportError:
    warnings.warn('Missing optional caching backends dependency, '
                  'Some backends will not be available')
