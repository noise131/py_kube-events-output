# encoding: utf-8

"""
    @Author
        noise131
    @Desc
        主要运行文件
    @Date
        2022-09-05 10:34:03
    @Ver
        v1.0
    @PyVer
        3.10.x (3.10.5)
    @Github
        https://github.com/noise131
"""

from GlobalConfig import GlobalConfig
import time
import logging
import json
from multiprocessing import Process, Queue
from kube_event import event_collect
from event_output import file, mongo, elastic
from threading import Thread

if __name__ == '__main__':
    logger = logging.getLogger('{}.main'.format(GlobalConfig.project_name))
    event_queue = Queue(2000)
    event_mongo = mongo.mongo(**GlobalConfig.mongo_conn_info)
    if 'file' in GlobalConfig.output:
        event_file = file.file(GlobalConfig.event_record_file)
    event_collect_p = Process(target=event_collect, args=(GlobalConfig.kube_config_file,
                                                        event_queue, GlobalConfig.kube_cluster_name),
                                                        kwargs={'timezone': GlobalConfig.timezone})
    event_collect_p.start()
    while True:
        try:
            r = event_queue.get()
        except Exception as e:
            logger.critical('主进程读取队列数据失败')
            raise
        if not r:
            logger.critical('主进程结束')
            time.sleep(2)
            break
        logger.debug('成功从队列中取出数据')
        if event_mongo.doc_exist_check({'uid': r.get('uid'), 'time': r.get('time')}):
            logger.debug('事件在数据库中已存在')
            continue
        write_t_list = []
        mongo_write_t = Thread(target=event_mongo.doc_write_one, args=(r,))
        mongo_write_t.start()
        write_t_list.append(mongo_write_t)
        if 'file' in GlobalConfig.output:
            file_t = Thread(target=event_file.event_write_file, args=(json.dumps(dict(r)),))
            file_t.start()
            write_t_list.append(file_t)
        for t in write_t_list:
            t.join()

