from abc import ABCMeta, abstractmethod

from production.model import ProductionOrder


class OrderCondition(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def evaluate(self, order):
        # type: (ProductionOrder) -> bool
        raise NotImplementedError()
