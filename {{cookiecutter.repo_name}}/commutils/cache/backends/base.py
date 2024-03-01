from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union

Key = Union[bytes, str]


class BaseCache(object):
    """ 缓存基类

    """

    def __init__(self, dexp):
        self._config = {"dexp": dexp}  # default expire time second

    def set(self, key, value, expire: Union[int, float] = None) -> Optional[bool]:
        raise NotImplementedError()

    def set_many(self, values: Dict[Key, Any], expire: Union[int, float] = None, keep_type=True) -> List[Key]:
        raise NotImplementedError()

    def get(self, key) -> Any:
        raise NotImplementedError()

    def get_many(self, keys: Iterable[Key]) -> Dict[Key, Any]:
        raise NotImplementedError()

    def replace(self, key, value, expire: Union[int, float]) -> bool:
        raise NotImplementedError()

    def delete(self, *keys) -> bool:
        raise NotImplementedError()

    def flush_all(self) -> bool:
        raise NotImplementedError()

    def update_cfg(self, **cfg_kwags):
        self._config.update(cfg_kwags)
