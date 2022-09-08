# encoding: utf-8

"""
    @Author
        noise131
    @Desc
        事件写入 mongodb 操作
    @Date
        2022-09-04 16:25:10
    @Ver
        v1.0
    @PyVer
        3.10.x (3.10.5)
    @Github
        https://github.com/noise131
"""

import logging
import sys
import time
from GlobalConfig import GlobalConfig
from datetime import datetime
from pymongo import MongoClient, collection, database

logger = logging.getLogger('{}.{}'.format(GlobalConfig.project_name, __name__))

class mongo():
    mongo_conn: MongoClient = None
    mongo_db: database.Database = None
    mongo_coll: collection.Collection = None
    __mongo_conn_url: str = None
    __mongo_dbname: str = None
    __mongo_collection_origin: str = None
    __mongo_collection: str = None
    __coll_rotate_lock: bool = False
    # __mongo_host: str = None
    # __mongo_port: str = None
    # __mongo_username: str = None
    # __mongo_password: str = None
    # __mongo_scheme: str = None
    # __mongo_auth_db: str = None
    # __options: list = None

    def __init__(self, host: str = 'localhost', port: str = '27017',
                username: str = None, password: str = None, scheme: str = 'mongodb',
                dbname: str = 'admin', options: list = '', collection: str = 'coll_test',
                retry: int = 1) -> None:
        self.__mongo_dbname = dbname
        self.__mongo_collection_origin = collection
        self.__mongo_collection = '{}_{}'.format(self.__mongo_collection_origin,
                                                    datetime.now().strftime(r'%Y_%m_%d'))
        if username is not None and password is not None:
            auth_info = '{}:{}@'.format(username, password)
        if options:
            options = '?{}'.format('&'.join(options))
        self.__mongo_conn_url = '{}://{}{}:{}/{}{}'.format(scheme, auth_info,
                                                            host, port, dbname, options)
        if not self.__mongo_connect_test(retry):
            raise Exception('mongodb 连接失败已达到最大重试次数 : {}'.format(retry))

    # TODO : 待重构, 失败达到最大次数直接抛出异常
    def __mongo_connect_test(self, retry: int) -> bool:
        for i in range(retry):
            logger.info('尝试第 {} 次连接 mongodb'.format(i + 1))
            try:
                self.mongo_conn = MongoClient(self.__mongo_conn_url)
                self.mongo_db = self.mongo_conn.get_database(self.__mongo_dbname)
                self.mongo_coll = self.mongo_db.get_collection(self.__mongo_collection)
                info = self.mongo_conn.server_info()
                logger.info('mongodb 连接成功')
                logger.debug('mongodb 连接信息 : {}'.format(self.mongo_conn))
                logger.debug('mondofb 连接 url : {}'.format(self.__mongo_conn_url))
                logger.debug('mongodb 服务器信息 : {}'.format(dict(info)))
            except Exception as e:
                logger.error('mongodb 连接失败 : {}'.format(str(e)))
                if i == retry - 1:
                    return False
                time.sleep(5)
                continue
            return True

    # TODO : 判断传参有效性, 列表 和 字典
    # TODO : 添加等待轮换锁功能
    # TODO : 添加连接失败自动重连功能
    def doc_write_one(self, docs: list | dict):
        # id = self.doc_increase_id()
        docs = docs.copy()
        try:
            if type(docs) is dict:
                # docs['_id'] = id
                self.mongo_coll.insert_one(docs)
                logger.info('单条事件写入 mongodb : {}'.format(docs))
            else:
                self.mongo_coll.insert_many(docs)
                logger.info('多条事件写入 mongodb : {}'.format(docs))
        except Exception as e:
            self.write_error(e)
            raise

    # 该功能暂时弃用
    def doc_increase_id(self) -> int:
        try:
            select_r = self.mongo_coll.find().sort('_id', -1).limit(1)
        except Exception as e:
            self.select_error(e)
            raise
        id = 1
        for i in select_r:
            id = i.get('_id') + 1
        return id

    def doc_exist_check(self, where: dict) -> bool:
        try:
            select_r = self.mongo_coll.find_one(where)
        except Exception as e:
            self.select_error(e)
            raise
        if select_r:
            return True
        return False

    def coll_rotate(self) -> bool:
        self.__coll_rotate_lock = True
        self.__mongo_collection = '{}_{}'.format(self.__mongo_collection_origin,
                                                    datetime.now().strftime(r'%Y_%m_%d'))
        self.mongo_coll = self.mongo_db.get_collection(self.__mongo_collection)
        self.__coll_rotate_lock = False

    def select_error(self, exception) -> None:
        logger.critical('mongodb 查询数据时出错 : {}, 数据库 : {}, 集合 : {}'.format(exception, self.__mongo_dbname, self.__mongo_collection))

    def write_error(self, exception) -> None:
        logger.critical('mongodb 写入数据时出错 : {}, 数据库 : {}, 集合 : {}'.format(exception, self.__mongo_dbname, self.__mongo_collection))

    @property
    def dbname(self) -> str:
        return self.__mongo_dbname

    @property
    def collection(self) -> str:
        return self.__mongo_collection

    @property
    def connect_url(self) -> str:
        return self.__mongo_conn_url

    @property
    def coll_rotate_lock(self) -> bool:
        return self.__coll_rotate_lock


