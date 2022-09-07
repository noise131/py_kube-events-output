# encoding: utf-8

"""
    @Author
        noise131
    @Desc
        kubernetes 事件日志收集
    @Date
        2022-09-04 18:34:07
    @Ver
        v1.0
    @PyVer
        3.10.x (3.10.5)
    @Github
        https://github.com/noise131
"""


from queue import Full
from multiprocessing import Queue
from kubernetes import client, config, watch
import datetime
import time
import logging
import arrow
import urllib3
from GlobalConfig import GlobalConfig

logger = logging.getLogger('{}.{}'.format(GlobalConfig.project_name, __name__))

def uid_check_record(uid: str, uid_list: list, index: int, cache_len: int) -> tuple[bool, int]:
    if uid in uid_list:
        logger.debug('重复事件 : {}, 已丢弃'.format(uid))
        return (True, index)
    if index == cache_len:
        logger.debug('事件 uid 缓存达到 {} 自动轮换'.format(cache_len))
        index = 0
    logger.debug('新事件 : {}, 已添加 uid 到缓存, 位置 : {}'.format(uid, index))
    uid_list[index] = uid
    return (False, index + 1)

def cluster_connect_test(retry: int, kube_api: client.CoreV1Api, timeout: int, conn_timeout: int) -> bool:
    for i in range(retry):
        logger.info('尝试第 {} 次连接 kubernetes 集群'.format(i + 1))
        try:
            kube_api.list_namespace(timeout_seconds=timeout, _request_timeout=timeout)
            logger.info('kubernetes 集群连接成功')
        except Exception as e:
            logger.error('连接失败 : {}'.format(str(e)))
            if i == retry - 1:
                logger.critical('kubernetes 连接已达到最大重试次数')
                return False
            logger.info('等待下一次连接')
            time.sleep(conn_timeout)
            continue
        return True

def event_collect(kube_conf_path: str, event_q: Queue, kube_cluster_name: str,
                    timeout: int = 3, retry: int = 3, timezone: int = 0) -> None:
    config.load_kube_config(config_file=kube_conf_path)
    v1 = client.CoreV1Api()
    w = watch.Watch()
    uid_list: list = [None] * 1000
    list_index = 0
    logger.info('开始连接 kubernetes 集群 : {}'.format(kube_cluster_name))
    while True:
        if not cluster_connect_test(retry, v1, timeout, GlobalConfig.kube_conn_wait):
            logger.critical('kubernetes 连接已达到最大重试次数 {}'.format(retry))
            event_q.put(None)
            break
        try:
            logger.info('开始监听事件')
            for event in w.stream(v1.list_event_for_all_namespaces):
                # print(event)
                try:
                    event_uid = event.get('object').metadata.uid
                    check_result = uid_check_record(event_uid, uid_list, list_index, GlobalConfig.event_uid_cache_len)
                    if check_result[0]:
                        continue
                    list_index = check_result[1]
                    time = arrow.Arrow.fromdatetime(event.get('object').metadata.creation_timestamp).datetime
                    if timezone:
                        time = time.astimezone(datetime.timezone(datetime.timedelta(hours=timezone)))
                    event_struce = {
                        'message': event.get('object').message,
                        'reason': event.get('object').reason,
                        'type': event.get('object').type,
                        'api_version': event.get('object').api_version,
                        'namespace': event.get('object').metadata.namespace,
                        'involved_object': {
                            'kind': event.get('object').involved_object.kind,
                            'name': event.get('object').involved_object.name
                        },
                        'time': time.strftime(r'%Y-%m-%dT%H:%M:%S%z'),
                        'uid': event.get('object').metadata.uid
                    }
                except Exception as e:
                    print('转换出错 : {}'.format(str(e)))
                    continue
                try:
                    event_q.put(event_struce, timeout=5)
                except Full:
                    logger.critical('队列已满, 检查消费模块是否发生故障')
                    event_q.put(None)
                    raise
                except Exception:
                    logger.critical('事件发送到队列时出现异常')
                    event_q.put(None)
                    raise
                logger.debug('事件 {}, 已加入队列'.format(event_uid))
                # print(event_struce)
        except urllib3.exceptions.ProtocolError as e:
            logger.info('kubernetes 常规重连')
        except Exception as e:
            logger.warning('异常重连 : {}'.format(str(e)))

if __name__ == '__main__':
    q = Queue()
    event_collect(kube_conf_path=GlobalConfig.kube_config_file,
                    event_q=q, kube_cluster_name=GlobalConfig.kube_cluster_name,
                    timezone=GlobalConfig.timezone)
