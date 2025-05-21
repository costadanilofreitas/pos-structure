from abc import ABCMeta, abstractmethod

from production.model import ProductionOrder


class PublishScheduler(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def schedule_publish(self, order, wait_time):
        # type: (ProductionOrder, int) -> None
        raise NotImplementedError()
