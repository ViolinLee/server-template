""" 支持目标函数结果返回的多线程装饰器

修改自该项目: https://github.com/cocuni80/thread_decorator
"""

import threading
from typing import Union, List


class ResultThread(threading.Thread):
    """ 支持目标函数结果返回的线程类
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.result = None
        self.error = None

    def run(self, *args, **kwargs):
        try:
            if self._target:
                self.result = self._target(*self._args, **self._kwargs)
        except Exception as e:
            self.error = e
        finally:
            del self._target, self._args, self._kwargs

    def wait_output(self):
        """ 等待目标函数输出结果 (非异步、将阻塞主线程)
        """
        self.join()
        return self.result

    def get_error(self):
        """ 若发生异常则返回的Exception否则返回None
        """
        self.join()
        return self.error


def threaded(daemon=False, start=True):
    """ 多线程装饰器

    [创建]并[启动]线程任务
    :param daemon: 是否作为守护进程线程运行
    :param start: 是否在进程创建后自动开启任务
    :return:
    """

    def _threaded(func):
        def wrapper(*args, **kwargs):
            thread = ResultThread(target=func, daemon=daemon, args=args, kwargs=kwargs)
            if start:
                thread.start()
            return thread

        return wrapper

    return _threaded


@threaded(False, True)
def run_threaded(func, *args, **kwargs):
    """ 适用于将第三方函数多线程化的辅助函数 (自动开启任务)
    :param func: 需在独立线程中执行的目标函数
    :param args: 接收func的位置参数 (列表)
    :param kwargs: 接收func的关键字参数 (字典)
    :return:
    """
    return func(*args, **kwargs)


@threaded(False, False)
def run_threaded_pending(func, *args, **kwargs):
    """ 适用于将第三方函数多线程化的辅助函数 (不会自动开启任务)
    :param func: 需在独立线程中执行的目标函数
    :param args: 接收func的位置参数 (列表)
    :param kwargs: 接收func的关键字参数 (字典)
    :return:
    """
    return func(*args, **kwargs)


class MultiThreadManager(object):
    """ 适配ResultThread的多线程管理器
    支持将多个线程目标函数的返回值存储在列表中并返回
    """
    threads = []

    def __init__(self, threads: ResultThread = None):
        """
        :param threads: a list of ResultThread objects
        :return: None
        """
        self.threads = threads if threads is not None else []

    def add_thread(self, thread: Union[ResultThread, List[ResultThread]]):
        """ 往线程列表添加ResultThread实例
        :param thread: ResultThread实例 (支持传入列表)
        :return: None
        """
        if isinstance(thread, ResultThread):
            self.threads.append(thread)
        elif isinstance(thread, list) and all(isinstance(t, ResultThread) for t in thread):
            self.threads.extend(thread)
        else:
            raise TypeError("thread must be a ResultThread instance or a list of ResultThread instances")

    def get_threads(self):
        """ 获取管理器所有线程的列表 (列表的ResultThread按添加顺序排列)
        :return:
        """
        return self.threads

    def start_all(self):
        """ 启动所有线程,将忽视开启过程中的异常
        """
        for t in self.threads:
            try:
                t.start()
            except RuntimeError:
                pass

    def wait_output(self):
        """ 等待线程管理器的所有线程都执行完成 (将阻塞主线程)
        :return: list of objects
        """
        results = []
        for t in self.threads:
            results.append(t.wait_output())
        return results


def run_chunked(func, dataset, threads=8, args=(), kwargs={}):
    """ 数据分批多线程处理的辅助函数
    :param func: 数据处理函数
    :param dataset: 数据集
    :param threads: 线程数
    :param args: 接收func的位置参数 (列表)
    :param kwargs: 接收func的关键字参数 (字典)
    :return: 线程管理器MultiThreadManager实例
    """
    chunks = []
    for i in range(0, len(dataset), threads):
        chunks.append(dataset[i:i + threads])
    manager = MultiThreadManager()
    for chunk in chunks:
        manager.add_thread(run_threaded(func, chunk, *args, **kwargs))

    return manager


if __name__ == '__main__':
    # unit test
    import time

    @threaded(False)  # 必传参数
    def delay_print(a, b, c='Love'):
        time.sleep(1)
        print(a + c + b)


    def delay_print_extra(a, b, c='Love'):
        time.sleep(1)
        print(a + c + b)


    print("start calling [delay_print]...")
    delay_print('I', 'You\n')
    print("end calling [delay_print].")

    print("start calling [delay_print_extra]...")
    run_threaded(delay_print_extra, 'I', 'You\n')
    print("end calling [delay_print_extra].")
