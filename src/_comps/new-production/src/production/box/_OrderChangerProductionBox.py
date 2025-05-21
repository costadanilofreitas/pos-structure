from abc import ABCMeta, abstractmethod

from production.box import ProductionBox
from production.model import ProductionOrder


class OrderChangerProductionBox(ProductionBox):
    __metaclass__ = ABCMeta

    def order_modified(self, order):
        self.debug("{} - Order before modification:\n{}", self.name, str(order))

        altered_order = self.change_order(order)
        if altered_order is not None:
            self.debug("{} - Order after modification:\n{}", self.name, str(altered_order))
            self.send_to_children(order)
        else:
            self.debug("{} - Order removed", self.name)

    @abstractmethod
    def change_order(self, order):
        # type: (ProductionOrder) -> ProductionOrder
        raise NotImplementedError()
