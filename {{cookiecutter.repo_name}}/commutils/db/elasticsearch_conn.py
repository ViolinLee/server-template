""" ES连接封装类

elasticsearch-py 默认使用连接池来管理连接，并提供了一些控制选项，如连接的最大存活时间、最大空闲时间和连接数量等
"""

from typing import Union, Sequence, List, Dict, Any
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from commutils.parser.conf_parser import ConfigAgent


class ESConnection:
    def __init__(self, hosts, *args, **kwargs):
        """
        :param hosts:
        :param args:
        :param kwargs: 建议参数:

        """
        self._es = Elasticsearch(hosts, *args, **kwargs)

    @property
    def es_conn(self):
        return self._es

    @classmethod
    def from_conf(cls, filename, section):
        config_agent = ConfigAgent()
        config_agent.read(filename)
        kwargs = config_agent.get_dict(section)

        hosts_str = kwargs['hosts']
        host_list = [hosts_str] if ',' not in hosts_str else hosts_str.split(',')
        http_auth = [kwargs['username'], kwargs['password']]

        return cls(ESConnection.concat_host_auth(host_list, http_auth))

    @staticmethod
    def concat_host_auth(hosts, auth: Sequence):
        """ 返回Elasticsearch构造函数hosts参数的数据

        :param hosts: [域名:端口, ...]
        :param auth: (名称,密码)
        :return:
        """
        hosts = hosts if isinstance(hosts, list) else [hosts]
        return ["http://" + auth[0] + ':' + auth[1] + '@' + host for i, host in enumerate(hosts)]

    def create_index(self, index_name, settings=None, mappings=None):
        """ 创建一个新的索引

        :param index_name:
        :param settings:
        :param mappings:
        :return:
        """
        if not self._es.indices.exists(index_name):
            self._es.indices.create(index=index_name, body={"settings": settings, "mappings": mappings})

    def delete_index(self, index_name):
        """ 删除一个旧索引

        :param index_name:
        :return:
        """
        if self._es.indices.exists(index_name):
            self._es.indices.delete(index=index_name)

    def index_document(self, index_name, document, doc_id=None):
        """ 添加一条记录

        :param index_name:
        :param document:
        :param doc_id:
        :return:
        """
        self._es.index(index=index_name, body=document, id=doc_id)

    def bulk_batch(self, data: List[Dict[str, Any]] = []):
        """ 批量添加文档

        :param data: 数据源
        :return:
        """
        bulk(self._es, data)

    def get_document(self, index_name, doc_id):
        """ 索引一条文档记录

        :param index_name:
        :param doc_id:
        :return:
        """
        return self._es.get(index=index_name, id=doc_id)

    def update_document(self, index_name, doc_id, document):
        """ 更新文档

        :param index_name:
        :param doc_id:
        :param document:
        :return:
        """
        self._es.update(index=index_name, id=doc_id, body=document)

    def delete_document(self, index_name, doc_id):
        """ 删除一条文档

        :param index_name:
        :param doc_id:
        :return:
        """
        self._es.delete(index=index_name, id=doc_id)

    def search(self, index_name, query, size=10, from_=0):
        """ 通用查询

        :param index_name:
        :param query:
        :param size:
        :param from_:
        :return:
        """
        return self._es.search(index=index_name, body=query, size=size, from_=from_)

    def search_with_scroll(self, index_name, query, size=1000, scroll="5m", batch: bool = True, page: int = None):
        """ 滚动查询: 用于处理大量数据的分页查询

        :param index_name: 索引名称
        :param query: 请求体,例 {'query': {'match_all': {}}, 'size': 100, 'sort': ['_doc']}
        :param size: 结果文档数量,会覆盖query.size (若有)
        :param scroll: 结果集缓存时间
        :param batch: 是否批量返回:是-返回list,否-返回单个doc
        :param page: 限定的滚动查询次数,从1开始
        :return:
        """
        cur_page = 1
        response = self._es.search(index=index_name, body=query, size=size, scroll=scroll)

        try:
            while True:
                if batch:
                    yield response['hits']['hits']
                else:
                    for hit in response['hits']['hits']:
                        yield hit

                scroll_id = response.get('_scroll_id')
                if scroll_id and (page is None or page > cur_page):
                    response = self._es.scroll(scroll_id=scroll_id, scroll=scroll)

                    # 该次查询结果为空则结束滚动
                    if not response['hits']['hits']:
                        break

                    cur_page += 1
                else:
                    break
        except:
            raise
        finally:
            self._es.clear_scroll(scroll_id=scroll_id)


if __name__ == '__main__':
    """
    参考:https://dylancastillo.co/elasticsearch-python/#create-an-index
    数据下载:https://www.kaggle.com/datasets/jrobischon/wikipedia-movie-plots?resource=download
    """

    import json
    import pandas as pd

    INDEX_NAME = "example-movies"
    ES_HOST_DEV = ["es-test01.roboticscv.com:9600", "es-test02.roboticscv.com:9600", "es-test03.roboticscv.com:9600"]
    HTTP_AUTH_DEV = ('roboticscv', 'fceb8c9716d3ee4')

    # 建立连接
    # client = ESConnection(hosts=ESConnection.concat_host_auth(ES_HOST_DEV, HTTP_AUTH_DEV))
    client_conf = ESConnection.from_conf("example_db.conf", "es-dev")
    print(client_conf.es_conn.info())

    # ######################################################↓数据准备↓####################################################
    """
    # 创建索引
    settings = {"number_of_shards": 5, "number_of_replicas": 1}
    mappings = {
        "_doc": {
            "properties": {
                "title": {"type": "text", "analyzer": "english"},
                "ethnicity": {"type": "text", "analyzer": "standard"},
                "director": {"type": "text", "analyzer": "standard"},
                "cast": {"type": "text", "analyzer": "standard"},
                "genre": {"type": "text", "analyzer": "standard"},
                "plot": {"type": "text", "analyzer": "english"},
                "year": {"type": "integer"},
                "wiki_page": {"type": "keyword"}
            }
        }
    }
    client_conf.create_index(INDEX_NAME, settings=settings, mappings=mappings)

    # 准备数据源
    df = pd.read_csv("../wiki_movie_plots_deduped.csv").dropna().sample(5000, random_state=42).reset_index()
    print(f"读取的源数据总数: {df.shape[0]}条")

    # 手动添加一条记录
    doc = {
        "title": ["The rise of the son"],
        "ethnicity": ["Han"],
        "director": ["RoboticsCV"],
        "cast": ["LeeChan,SophiaChan"],
        "genre": ["documentary"],
        "plot": ["Being Rich"],
        "year": ["2024"],
        "wiki_page": ["https://roboticscv.com"]
    }
    client_conf.index_document(index_name=INDEX_NAME, doc_id=5000, document=doc)
    print(f"手动插入1条文档")

    # 批量添加数据
    bulk_data = []
    for i, row in df.iterrows():
        bulk_data.append(
            {
                "_index": INDEX_NAME,
                "_type": "_doc",
                "_id": i,
                "_source": {
                    "title": row["Title"],
                    "ethnicity": row["Origin/Ethnicity"],
                    "director": row["Director"],
                    "cast": row["Cast"],
                    "genre": row["Genre"],
                    "plot": row["Plot"],
                    "year": row["Release Year"],
                    "wiki_page": row["Wiki Page"],
                }
            }
        )
    client_conf.bulk_batch(bulk_data)
    print(f"批量插入{len(bulk_data)}条数据")
    """
    # ######################################################↑数据准备↑####################################################

    # 搜索文档
    search_request = {
        'query': {'match_all': {}},
        'size': 5,
        'sort': ['_doc']
    }
    search_results = client_conf.search(INDEX_NAME, search_request, size=10)
    print("搜索结果:")
    print(json.dumps(search_results, indent=4, ensure_ascii=False))

    # 使用滚动搜索处理大量数据（逐个文档返回）
    cnt_doc = 0
    for doc_hit in client_conf.search_with_scroll(INDEX_NAME, search_request, size=2, batch=False, page=3):
        print(f"第{cnt_doc}条:")
        print(doc_hit)
        cnt_doc += 1

    # 使用滚动搜索处理大量数据（批量返回,需要手动控制查询页数,否则遍历直至数据为空）
    cnt = 0
    for hits in client_conf.search_with_scroll(INDEX_NAME, search_request, size=10, batch=True):
        print(f"第{cnt}轮:")
        print(hits)

        if cnt == 2:
            break
        cnt += 1

    # 使用滚动搜索处理大量数据（批量返回,自动限制页数）
    cnt_page = 0
    for hits in client_conf.search_with_scroll(INDEX_NAME, search_request, size=10, batch=True, page=3):
        print(f"第{cnt_page}轮:")
        print(hits)
        cnt_page += 1

    # 滚动查询边界测试
    cnt_page = 0
    for hits in client_conf.search_with_scroll(INDEX_NAME, search_request, size=1000, batch=True):
        print(f"第{cnt_page}轮:")
        print(len(hits))
        cnt_page += 1
