from mw_helper import ensure_iterable, convert_to_dict
from production.box._OrderChangerProductionBox import OrderChangerProductionBox
from production.model import ProdStates


class OrderStateFilterBox(OrderChangerProductionBox):
    def __init__(self, name, sons, allowed_order_states, excluded_order_states, logger=None):
        super(OrderStateFilterBox, self).__init__(name, sons, logger)
        self.allowed_order_states = convert_to_dict(ensure_iterable(allowed_order_states))
        self.excluded_order_states = convert_to_dict(ensure_iterable(excluded_order_states))

    def change_order(self, order):
        if self.should_filter_order(order):
            order.prod_state = ProdStates.INVALID

        return order

    def should_filter_order(self, order):
        if self.allowed_order_states and order.state not in self.allowed_order_states:
            return True
        if self.excluded_order_states and order.state in self.excluded_order_states:
            return True
        return False
