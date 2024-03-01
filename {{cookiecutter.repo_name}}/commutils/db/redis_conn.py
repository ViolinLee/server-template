""" Redis单机/集群连接池

依赖：redis-3.5.3 redis-py-cluster-2.1.3 (latest version, 2024起不再维护)
"""

import redis
from rediscluster import RedisCluster, ClusterBlockingConnectionPool

from typing import Union
from commutils.parser.conf_parser import ConfigAgent


class RedisPool:
    """ Redis连接池类

    注：未测试中途连接断开是否自动重连
    """
    def __init__(self, url: str = None, is_cluster: bool = False, **kwargs):
        self.is_cluster = is_cluster

        self._conn_pool = None
        self.conn: Union[redis.StrictRedis, ClusterBlockingConnectionPool] = None

        if url:
            self._connect_url(url, **kwargs)
        elif is_cluster:
            self._connect_cluster(**kwargs)
        else:
            self._connect_single_node(**kwargs)

    @classmethod
    def from_conf(cls, filename, section):
        """ 从文件读取配置并返回已建立连接的RedisPool对象

        支持单机和集群配置
        :param filename:
        :param section:
        :return:
        """
        config_agent = ConfigAgent()
        config_agent.read(filename)
        kwargs = config_agent.get_dict(section)
        is_cluster = True if "host" in kwargs.keys() and len(kwargs["host"].split(',')) > 1 else False

        return cls(None, is_cluster, **kwargs)

    @classmethod
    def from_url(cls, url, db=None, decode_components=False, **kwargs):
        """ 根据传入URL建立连接并返回RedisPool对象

        参数db和decode_components是为兼容【redis.ConnectionPool.from_url】方法接口
        :param url:
        :param db:
        :param decode_components:
        :param kwargs:
        :return:
        """
        assert url is not None, "URL参数不能为空"

        kwargs['db'] = db
        kwargs['decode_components'] = decode_components

        return cls(url, False, **kwargs)

    def _connect_url(self, url, **kwargs):
        """ 通过指定URL连接

        不支持集群
        :return:
        """
        self._conn_pool = redis.ConnectionPool.from_url(url, **kwargs)
        self.conn = redis.StrictRedis(connection_pool=self._conn_pool)

    def _connect_single_node(self, **kwargs):
        """ 单机版连接池

        建议应配置项: host port password db decode_responses(True)
        :param args:
        :param kwargs:
        :return:
        """
        self._conn_pool = redis.ConnectionPool(**kwargs)
        self.conn = redis.StrictRedis(connection_pool=self._conn_pool)

    def _connect_cluster(self, **kwargs):
        """ 集群版连接池

        建议配置项:
            startup_nodes(dict), password, db, decode_responses(True), max_connections(12),
            skip_full_coverage_check(True), max_connections_per_node(True), health_check_interval(50)
            socket_timeout(3), socket_connect_timeout(15), socket_keepalive(True)
        :param args:
        :param kwargs:
        :return:
        """

        if 'startup_nodes' not in kwargs.keys():
            hosts = kwargs.pop('host').split(',')
            ports = kwargs.pop('port')
            ports = [ports] * len(hosts) if str(ports).isdigit() else list(map(int, ports.split(',')))
            assert len(hosts) == len(ports), "配置错误:请检查集群主机与端口的配置"

            kwargs['startup_nodes'] = [{'host': host, 'port': ports[i]} for i, host in enumerate(hosts)]
        print(kwargs)

        self._conn_pool = ClusterBlockingConnectionPool(**kwargs)
        self.conn = RedisCluster(connection_pool=self._conn_pool)

    """以下提供常用操作方法封装。也可以直接使用实例的conn属性来调用"""
    def set(self, name, value, ex=None, px=None, nx=False, xx=False, keepttl=False):
        return self.conn.set(name, value, ex, px, nx, xx, keepttl)

    def mset(self, mapping):
        return self.conn.mset(mapping)

    def get(self, name):
        return self.conn.get(name)

    def mget(self, keys, *args):
        return self.conn.mget(keys, *args)

    def delete(self, *names):
        return self.conn.delete(*names)

    def pipeline(self, transaction=True, shard_hint=None):
        return self.conn.pipeline(transaction, shard_hint)


if __name__ == '__main__':
    import time

    # 测试单机模式
    TEST_SINGLE_NODE = True
    # 测试通过URL建立连接
    TEST_FROM_URL = False
    # 测试读取配置文件
    TEST_FROM_CONF = True

    if TEST_SINGLE_NODE:
        # Single Node
        if TEST_FROM_URL:
            redis_pool = RedisPool.from_url("redis://localhost:6379/1", decode_responses=True)
        elif TEST_FROM_CONF:
            redis_pool = RedisPool.from_conf("example_db.conf", "redis-single-node")
        else:
            redis_pool = RedisPool(None, False, host='localhost', port=6379, db=1, decode_responses=True)
    else:
        # Cluster
        if TEST_FROM_CONF:
            redis_pool = RedisPool.from_conf("example_db.conf", "redis-cluster")
        else:
            redis_pool = RedisPool(None, True,
                                   startup_nodes=[{'host': 'redis01.dev.roboticscv.com', 'port': 7000},
                                                  {'host': 'redis02.dev.roboticscv.com', 'port': 7000},
                                                  {'host': 'redis03.dev.roboticscv.com', 'port': 7000}],
                                   password='7hGFTyhs6538', db=0, decode_responses=True)  # 注:其它db无权限

    redis_pool.set('FOREVER', 1314)
    print("GET: ", redis_pool.get('FOREVER'))
    redis_pool.set('GOOGLE', 'google')
    redis_pool.set('DJI', 'dji', ex=3)
    print("MGET: ", redis_pool.mget(['GOOGLE', 'DJI', 'FOREVER', 'NOT-EXIST']))  # 注:mget取出的值都是字符串格式,客户端需要自行转换
    time.sleep(3.5)
    print("EXPIRY: ", redis_pool.get('DJI'))
    redis_pool.delete('GOOGLE')
    print("DELETE: ", redis_pool.mget(['GOOGLE', 'DJI']))
