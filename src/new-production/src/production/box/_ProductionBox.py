from abc import ABCMeta, abstractmethod
from logging import Logger

from production.model import ProductionOrder
from typing import Dict, List, Optional, Union, Tuple


class ProductionBox(object):
    __metaclass__ = ABCMeta

    def __init__(self, name, sons, logger=None):
        # type: (str, Optional[Union[List[ProductionBox]], ProductionBox], Logger) -> None
        self.name = name
        if sons is None:
            self.sons = []
        elif isinstance(sons, List):
            self.sons = sons
        else:
            self.sons = [sons]
        self.logger = logger
        self.refreshing = False

        self.orders = {}  # type: Dict[Tuple[str, int], ProductionOrder]

    @abstractmethod
    def order_modified(self, order):
        # type: (ProductionOrder) -> None
        raise NotImplementedError()

    def send_to_children(self, order):
        # type: (ProductionOrder) -> None
        if self.sons is not None:
            for son in self.sons:
                son.order_modified(order)

    def handle_production_command(self, command):
        if self.sons is not None:
            handled = False
            for son in self.sons:
                if son.handle_production_command(command):
                    handled = True
            return handled
        else:
            return False

    def start_refresh(self):
        self.refreshing = True
        if self.sons is not None:
            for son in self.sons:
                son.start_refresh()

    def end_refresh(self):
        if self.sons is not None:
            for son in self.sons:
                son.end_refresh()
        self.refreshing = False

    def get_order(self, order_id):
        # type: (int) -> Optional[ProductionOrder]
        if (self.name, order_id) in self.orders:
            return self.orders[(self.name, order_id)]
        return None

    def save_order(self, order):
        # type: (ProductionOrder) -> None
        self.orders[(self.name, order.order_id)] = order

    def delete_order(self, order_id):
        # type: (int) -> None
        if (self.name, order_id) in self.orders:
            del self.orders[(self.name, order_id)]

    def debug(self, msg, *args):
        if self.logger is not None:
            msg = msg.format(*args).decode("utf-8")
            self.logger.debug(msg)
