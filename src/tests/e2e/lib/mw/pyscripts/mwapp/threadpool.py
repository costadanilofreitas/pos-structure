# Embedded file name: C:\Program Files\OpenSSH\gitlabci\mwapp\src\kernel\pyscripts\mwapp\threadpool.py
from Queue import Queue
from threading import Thread

class Worker(Thread):
    """ Worker(tasks, results) -> Worker
    
        This class represents a worker used in a thread pool. The worker waits
        for function tuples to be enqueued and calls them. The results are stored
        in a separate queue.
    
        @param tasks: {Queue.Queue} - function or "tasks" queue
        @param events: {Queue.Queue} - results queue
        @return: Worker instance.
    """

    def __init__(self, tasks, results):
        Thread.__init__(self)
        self.tasks = tasks
        self.results = results
        self.daemon = False
        self.start()

    def run(self):
        while True:
            func, args, kwargs, quit_flag = self.tasks.get()
            if quit_flag:
                break
            try:
                r = func(*args, **kwargs)
                self.results.put(r)
            except Exception as e:
                self.results.put(e)

            self.tasks.task_done()


class Pool(object):
    """ Pool(num_threads) -> Pool
    
        This class represents a simple thread pool that queues up
        functions to be called by a user specified amount of threads.
    
        @param num_threads: {int} - number of threads in pool
        @return: Pool instance.
    """

    def __init__(self, num_threads):
        self.tasks = Queue()
        self.results = Queue()
        self.workers = [ Worker(self.tasks, self.results) for _ in range(num_threads) ]

    def __del__(self):
        self.kill()

    def spawn(self, func, *args, **kargs):
        """  Add function to tasks queue """
        self.tasks.put((func,
         args,
         kargs,
         False))

    def join(self):
        """  Wait for all threads """
        self.tasks.join()

    def get_results(self):
        """  Get all results """
        results = []
        while not self.results.empty():
            r = self.results.get()
            if isinstance(r, Exception):
                raise r
            results.append(r)
            self.results.task_done()

        return results

    def kill(self):
        """  Kill all threads """
        for _ in range(len(self.workers)):
            self.tasks.put((None,
             (),
             {},
             True))

        return