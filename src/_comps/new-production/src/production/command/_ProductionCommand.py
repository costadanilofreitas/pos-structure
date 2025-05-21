from abc import ABCMeta, abstractmethod


class ProductionCommand(object):
    __metaclass__ = ABCMeta

    def __init__(self, order_id, view):
        self.order_id = order_id
        self.view = view

    @abstractmethod
    def get_hash_extra_value(self):
        # type: () -> str
        raise NotImplementedError()

    def __hash__(self):
        h = 0xcbf29ce484222325
        for c in "{}{}{}".format(self.order_id, self.view, self.get_hash_extra_value()):
            h *= 1099511628211
            h ^= ord(c)
        return h
