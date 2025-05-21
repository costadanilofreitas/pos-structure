from abc import ABCMeta, abstractmethod

from orderpump.model import OrderWithError
from typing import List


class OrderPumpRepository(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_last_order_sent(self):
        # type: () -> int
        raise NotImplementedError()

    @abstractmethod
    def set_last_order_processed(self, order_id):
        # type: (int) -> None
        raise NotImplementedError()

    def add_to_error(self, order_with_error):
        # type: (OrderWithError) -> None
        raise NotImplementedError()

    def update_order_with_error(self, order_with_error):
        # type: (OrderWithError) -> None
        raise NotImplementedError()

    def get_orders_with_error(self):
        # type: () -> List[OrderWithError]
        raise NotImplementedError()

    def mark_as_sent(self, order_id):
        # type: (OrderWithError) -> None
        raise NotImplementedError()
