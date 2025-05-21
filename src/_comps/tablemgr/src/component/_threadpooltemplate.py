# -*- coding: utf-8 -*-
# Module name: _threadpooltemplate.py
# Module Description: Thread pool template
#
# Copyright (C) 2018 MWneo Corporation
# Copyright (C) 2018 Omega Tech Enterprises Ltd. 
# (All rights transferred from MWneo Corporation to Omega Tech Enterprises Ltd.)
#
# $Id: _threadpooltemplate.py $
# $Revision: $
# $Date: $
# $Author: amerolli $

from Queue import Queue
from threading import Thread


class Worker(Thread):
    def __init__(self,queue):
        super(Worker, self).__init__()
        self._q = queue
        self.daemon = True
        self.start()

    def run(self):
        while True:
            f, args, kwargs = self._q.get()
            try:
                f(*args, **kwargs)
            except Exception as e:
                print(e)
            self._q.task_done()


class ThreadPool(object):
    def __init__(self, num_t=5):
        self._q = Queue(num_t)
        for _ in range(num_t):
            Worker(self._q)

    def add_task(self,f,*args,**kwargs):
        self._q.put((f, args, kwargs))
    
    def wait_complete(self):
        self._q.join()
