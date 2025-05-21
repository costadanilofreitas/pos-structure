from abc import ABCMeta, abstractmethod

from production.box import ProductionBox
from production.model import ProductionOrder, ProdStates


def _set_invalid_if_no_items(order):
    if not order.items:
        order.prod_state = ProdStates.INVALID


class OrderChangerProductionBox(ProductionBox):
    __metaclass__ = ABCMeta

    def order_modified(self, order):
        if not order.state:
            self.debug("{} - Order without state".format(self.name))

        self.debug("{} - Order before modification:\n{}", self.name, str(order))
        altered_order = self.change_order(order)
        if altered_order is not None:
            _set_invalid_if_no_items(altered_order)
            self.debug("{} - Order after modification:\n{}", self.name, str(altered_order))
            self.send_to_children(altered_order)
        else:
            self.debug("{} - Order removed", self.name)

    @abstractmethod
    def change_order(self, order):
        # type: (ProductionOrder) -> ProductionOrder

        raise NotImplementedError()
