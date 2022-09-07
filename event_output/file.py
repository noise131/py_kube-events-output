# encoding: utf-8

"""
    @Author
        noise131
    @Desc
        事件记录文件操作
    @Date
        2022-09-05 19:42:14
    @Ver
        v1.0
    @PyVer
        3.10.x (3.10.5)
    @Github
        https://github.com/noise131
"""

'''
import os,sys
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(base_dir)
sys.path.append(base_dir)
'''

import os
import sys
import logging
import time
from GlobalConfig import GlobalConfig

logger = logging.getLogger('{}.{}'.format(GlobalConfig.project_name, __name__))

class file():
    __file_path: str = None
    __file_name: str = None
    __file_path_complete: str = None
    __file_fp = None
    __rotate_lock = False

    def __init__(self, event_file_path: str) -> None:
        self.__file_path_complete = event_file_path
        file_path_handle = file.path_split(event_file_path)
        self.__file_path = file_path_handle[0]
        self.__file_name = file_path_handle[1]
        self.dir_create()
        try:
            self.__file_fp = open(event_file_path, 'a')
        except Exception as e:
            logger.critical('打开事件记录文件时出错')
            raise
            sys.exit(1)

    @ staticmethod
    def path_split(path: str) -> tuple[str, str]:
        '''
        分离文件路径中的路径和文件名

        :param path (str): 传递一个文件路径

        :return: 返回一个元组 tuple(file_path, file_name)
                    file_path (str) 存储文件路径\n
                    file_name (str) 存储文件名\n
                    如果分离出错返回 tuple(None, None)
        '''
        file_path = os.path.dirname(path)
        if not file_path:
            file_path = '.'
        file_path = ''.join([file_path, '/'])
        file_name = os.path.basename(path)
        return (file_path, file_name)

    def dir_create(self) -> bool:
        if not os.path.exists(self.__file_path):
            os.mkdir(self.__file_path)
        return True

    def event_write_file(self, content: list | str) -> bool:
        while True:
            if self.rotate_lock:
                time.sleep(0.5)
                continue
            if type(content) is str:
                content = [content]
            content_handle = []
            for row in content:
                if row[-1] == '\n':
                    content_handle.append(row)
                    continue
                content_handle.append(''.join([row, '\n']))
            try:
                self.__file_fp.writelines(content_handle)
                self.__file_fp.flush()
                logger.debug('事件写入文件成功')
                return True
            except Exception as e:
                logger.critical(''.join(['事件写入文件失败 : ', str(e)]))
                return False

    # TODO : 文件轮换
    def file_rotate(self) -> bool:
        self.__rotate_lock = True
        ...
        self.__rotate_lock = False

    @property
    def rotate_lock(self) -> bool:
        '''
        获取日志轮换锁
        '''
        return self.__rotate_lock

if __name__ == '__main__':
    test = file('./event_log/test.txt')
    test.event_write_file('1')
