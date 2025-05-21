from abc import ABCMeta, abstractmethod

from production.model import ProductionOrder
from typing import Callable


class OrderChanger(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def change_order(self, order_id, order_changer):
        # type: (int, Callable[[ProductionOrder], bool]) -> None
        raise NotImplementedError()
