from abc import ABCMeta, abstractmethod
from datetime import datetime

from production.model import ProductionOrder


class UndoCommand(object):
    __metaclass__ = ABCMeta

    def __init__(self, order_id, view):
        # type: (int) -> None
        self.order_id = order_id
        self.view = view

        self.enabled = True
        self.timestamp = datetime.now()

    @abstractmethod
    def undo(self, order):
        # type: (ProductionOrder) -> None
        raise NotImplementedError()

    def disable(self):
        self.enabled = False

    def enable(self):
        self.enabled = True

    def is_enabled(self):
        return self.enabled
