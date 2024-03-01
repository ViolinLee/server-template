""" 简易缓存模块,提供便捷的装饰器用法

亦可直接使用backends子模块下的缓存类
未手动设置缓存类时,装饰器默认使用字典缓存类DictCache
参考:
    https://github.com/lonetwin/supycache
"""


from .backends import DictCache
from .cdf import CacheDecoratorFactory


default_cache_backend = None


def get_default_backend():
    global default_cache_backend
    if not default_cache_backend:
        default_cache_backend = DictCache()
    return default_cache_backend


def set_default_backend(backend):
    global default_cache_backend
    default_cache_backend = backend


def easycache(**options):
    valid_options = {
        'backend',
        'cache_key',
        'expire_key',
        'ignore_errors',
    }

    if valid_options.isdisjoint(options):
        raise KeyError(f"Expecting optional arguments: {','.join(valid_options)}")

    backend = options.pop('backend', get_default_backend())

    return lambda function: CacheDecoratorFactory(backend, **options)(function)
