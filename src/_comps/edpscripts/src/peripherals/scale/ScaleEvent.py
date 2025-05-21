import threading


class ScaleEvent(object):
    def __init__(self):
        self.event = threading.Event()
        self.weight = None

    def set_weight(self, weight):
        self.weight = weight
        self.event.set()

    def wait(self, timeout):
        self.event.wait(timeout)
        self.event.clear()