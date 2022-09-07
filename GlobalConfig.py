# encoding: utf-8

"""
    @Author
        noise131
    @Desc
        全局配置
    @Date
        2022-09-04 20:26:59
    @Ver
        v1.0
    @PyVer
        3.10.x (3.10.5)
    @Github
        https://github.com/noise131
"""

import logging
from mimetypes import init
import time

class GlobalConfig():
    project_name: str = 'py_kube_events_output'

    log_level: int = 20

    timezone: int = +8

    event_uid_cache_len: int = 500

    kube_cluster_name = 'k8s-d-cluster'

    kube_config_file = r'admin.conf'

    kube_timeout: int = 3

    kube_conn_wait: int = 60

    init: bool = False

    mongo_conn_info: dict = {
        'host': '10.0.0.75',
        'port': '27017',
        'username': 'kubeevents',
        'password': 'kubeevents.123',
        'dbname': 'kubeevents',
        'collection': 'kubeevents',
        ## ['authSource=admin', 'replicaSet=mongors'] 会被转换为 ?authSource=admin&replicaSet=mongors
        'options': ['authSource=admin', 'serverSelectionTimeoutMS=3000'],
        'retry': 3
    }

    event_record_file: str = 'event_log/event.log'

    output: list = ['file', 'elasticsearch', 'logstash']

logger = logging.getLogger(GlobalConfig.project_name)
logger.setLevel(GlobalConfig.log_level)
log_sh = logging.StreamHandler()
logger.addHandler(log_sh)
log_format = logging.Formatter(fmt=r'%(asctime)s - [%(levelname)s] - %(name)s - %(process)s - %(thread)s - %(funcName)s - %(message)s',
                                datefmt=r'%Y-%m-%dT%H:%M:%S')
log_sh.setFormatter(log_format)
