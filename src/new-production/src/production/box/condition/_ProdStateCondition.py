from mw_helper import ensure_iterable

from ._OrderCondition import OrderCondition


class ProdStateCondition(OrderCondition):
    def __init__(self, prod_states):
        prod_states = ensure_iterable(prod_states)

        self.valid_prod_states = {}
        for prod_state in prod_states:
            self.valid_prod_states[prod_state] = prod_state

    def evaluate(self, order):
        return order.prod_state in self.valid_prod_states
