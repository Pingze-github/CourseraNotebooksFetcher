# -*- coding: utf-8 -*-

import time
import queue as Queue
import time
import traceback

import gevent
from gevent import Greenlet

from gevent import monkey
monkey.patch_all()
import requests

class XTask():
    def __init__(self, fn, args):
        self.fn = fn
        self.args = args

    def run(self):
        return self.fn(*self.args)

class XGreenlet(Greenlet):
    def __init__(self, queue):
        Greenlet.__init__(self)
        self.queue = queue
        self.seconds = 1
        self._running = True

    def _run(self):
        while True:
            if not self._running:
                break
            try:
                # 从队列中取出任务对象(非阻塞式)
                task = self.queue.get(block=False)

                # 执行任务
                task.run()

                self.queue.task_done()
            except Exception as e:
                # 队列取值失败，线程退出
                # 其他异常，打印错误栈
                if type(e) == Queue.Empty:
                    break
                else:
                    traceback.print_exc()
                    break

        self._running = False

class XGreenletPool():
    def __init__(self, queue, size):
        self.queue = queue
        self.greenlets = []

        for i in range(size):
            greenlet = XGreenlet(
                self.queue
            )
            self.greenlets.append(greenlet)

    def run(self, join=True):
        for greenlet in self.greenlets:
            greenlet.start()
        if join:
            self.__join()

    def __join(self):
        '''
        调用后，阻塞之后的代码
        :return:
        '''
        for greenlet in self.greenlets:
            greenlet.join()


if __name__ == '__main__':
    # 函数中必须使用gevent处理过的异步函数才有效果
    # for i in range(10):
    #     r = requests.get('http://127.0.0.1:9999/')
    #     print('Sync', r.status_code, r.text)

    def foo(a, b):
        # print('a+b', a, b)
        # gevent.sleep(1)
        # print('a+b=', a+b)
        # return a+b
        r = requests.get('http://127.0.0.1:9999/')
        print('Got baidu', r.status_code, r.text)

    q = Queue.Queue()

    for i in range(10):
        q.put(XTask(foo, [i, i+1]))

    pool = XGreenletPool(q, 10)

    start = time.time()

    # 默认阻塞
    pool.run()

    print('cost time', time.time() - start)

# TODO
# 0. 异常处理，异常不直接退出，而是以其他形式传递出来 => 可以手动try catch，不作特别处理
# 1. 设计一种优秀的机制来获取任务执行完毕的结果 => 1.存储结果，最后获取 2.通过event抛出
# 2. 支持简易调用，形成类似Promise.all()的效果 => gevent.joinall()就是，不必再实现
# 3. 结合async-await内置机制