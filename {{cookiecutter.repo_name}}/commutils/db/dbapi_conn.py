""" 通过封装DbUtils库提供对遵循DB API 2.0的第三方数据库驱动程序的通用操作

理论上支持的DB API 2.0驱动程序包括: pymysql/doris psycopg2 sqlite oracle sqlserver hbase
提供的通用操作:

参考：
    https://peps.python.org/pep-0249/#optional-db-api-extensions
    https://github.com/dapper91/generic-connection-pool
    https://webwareforpython.github.io/DBUtils/main.html
    https://github.com/jkklee/pymysql-pool/tree/master
"""

import importlib
from abc import abstractmethod
from contextlib import contextmanager

from DBUtils.PooledDB import PooledDB
from commutils.parser.conf_parser import ConfigAgent


class DBAPI2PoolBase:
    """ 符合DB API 2.0规范的连接池基类

    提供基本校验
    """

    def __init__(self, db_module_str, *args, **kwargs):
        self.driver = importlib.import_module(db_module_str)  # creator in PooledDB constructor

    @classmethod
    def from_conf(cls, db_module_str, filename, section):
        config_agent = ConfigAgent()
        config_agent.read(filename)
        kwargs = config_agent.get_dict(section)

        return cls(db_module_str, **kwargs)

    @staticmethod
    def from_params(db_module_str, *args, **kwargs):
        # 注意: 调用指定派生类的构造函数
        return DBUtilsPool(db_module_str, *args, **kwargs)

    @abstractmethod
    def _connect(self, args, kwargs):
        pass


class DBUtilsPool(DBAPI2PoolBase):
    """ 封装了DBUtils的连接池类

    连接的autocommit属性由用户配置决定,
    """

    def __init__(self, db_module_str, *args, **kwargs):
        super().__init__(db_module_str, *args, **kwargs)
        self._conn_pool: PooledDB = None
        self._connect(args, kwargs)

    def _connect(self, args, kwargs):
        self._conn_pool = PooledDB(creator=self.driver,
                                   mincached=0, maxcached=0,
                                   maxshared=0, maxconnections=0, blocking=False,
                                   maxusage=None, setsession=None, reset=True,
                                   failures=None, ping=1,
                                   *args, **kwargs)

    @contextmanager
    def get_cursor(self):
        conn = self._conn_pool.connection()
        try:
            # 注: 对于初始化时传递autocommit(False)的情况游标的某些方法可能需要手动提交事务
            # 此处连同"连接对象"一起返回,将某些需要手动控制"事务提交"的操作交由用户
            yield conn, conn.cursor()
        finally:
            conn.close()

    def get_one(self, query, args):
        """ 执行单次查询,返回单条记录

        注：仅适用于查询[select]场景

        :param query: 需要执行的查询语句
        :type query: str

        :param args: 查询参数
        :type args: tuple, list or dict

        :return: 单条查询记录
        """
        with self.get_cursor() as (conn, cursor):
            cursor.execute(query, args)
            return cursor.fetchone()

    def get_many(self, query, args, size=None):
        """ 执行单次查询,返回多条记录

        注：仅适用于查询[select]场景

        :param query: 需要执行的查询语句
        :type query: str

        :param args: 查询参数
        :type args: tuple, list or dict

        :param size: 最大返回记录数
        :type size: int

        :return: 多条查询记录
        """
        with self.get_cursor() as (conn, cursor):
            cursor.execute(query, args)

            if size is not None:
                return cursor.fetchmany(size)
            else:
                return cursor.fetchall()

    def query_batch(self, query, args):
        """ 批量执行多个相同结构的SQL语句,返回多条记录

        性能优于执行多次 ()
        注: cursor.executemany方法通常用于批量执行INSERT、UPDATE或DELETE语句，而不是SELECT语句

        :param query: 需要执行的查询语句
        :type query: str

        :param args: 查询参数
        :param args: tuple or list

        :return: 受影响的行数 (若有)
        """
        with self.get_cursor() as (conn, cursor):
            affected = cursor.executemany(query, args)
            conn.commit()
            return affected


if __name__ == '__main__':
    mysql_pool = DBUtilsPool.from_conf('pymysql', 'example_db.conf', 'mysql-dev')
    mysql_pool2 = DBUtilsPool.from_params('pymysql', host='localhost', port=3306, user='leechan', passwd='Cjdcst1314', autocommit=True)

    # 查询单条记录
    print(mysql_pool.get_one("SELECT * FROM testdb.debezium_demo", ()))
    # 查询多条记录
    print(mysql_pool.get_many("SELECT * FROM testdb.debezium_demo", ()))
    # 新增一条记录
    print(mysql_pool.get_one("INSERT INTO testdb.debezium_demo (id, name) VALUES (%s, %s)", ("8", "n8")))
    # 批量操作
    # print(mysql_pool2.query_batch("INSERT INTO testdb.debezium_demo (id, name) VALUES (%s, %s)",
    #                               [("14", "n14"), ("15", "n15")]))

