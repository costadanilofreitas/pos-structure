from abc import ABCMeta, abstractmethod

from salecomp.model import Line
from typing import Optional


class OrderRepository(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_order(self, pos_id, order_id):
        # type: (Optional[int], Optional[int]) -> Order
        raise NotImplementedError()

    @abstractmethod
    def add_line(self, line):
        # type: (Line) -> None
        raise NotImplementedError()

    @abstractmethod
    def update_line(self, line):
        # type: (Line) -> None
        raise NotImplementedError()

    @abstractmethod
    def delete_sons(self, line):
        # type: (Line) -> None
        raise NotImplementedError()
