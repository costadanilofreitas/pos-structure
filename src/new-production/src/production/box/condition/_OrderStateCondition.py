from mw_helper import ensure_iterable

from ._OrderCondition import OrderCondition


class OrderStateCondition(OrderCondition):
    def __init__(self, order_states):
        order_states = ensure_iterable(order_states)

        self.valid_order_states = {}
        for order_state in order_states:
            self.valid_order_states[order_state] = order_state

    def evaluate(self, order):
        return order.state in self.valid_order_states
