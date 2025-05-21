from abc import ABCMeta, abstractmethod
from datetime import datetime

from production.model import ProductionOrder
from typing import List


class ProductionRepository(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def save_order(self, order):
        # type: (ProductionOrder) -> None
        raise NotImplementedError()

    def get_all_orders(self):
        # type: () -> List[ProductionOrder]
        raise NotImplementedError()

    def get_orders_to_purge(self, limit_date):
        # type: (datetime) -> List[ProductionOrder]
        raise NotImplementedError()

    def purge_orders(self, orders):
        # type: (List[ProductionOrder]) -> None
        raise NotImplementedError()

    def purge_all_orders(self):
        # type: () -> None
        raise NotImplementedError()

    def stop(self):
        # type: () -> None
        raise NotImplementedError()
