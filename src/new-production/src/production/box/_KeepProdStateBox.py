from datetime import datetime
from mw_helper import ensure_iterable
from production.box._OrderChangerProductionBox import OrderChangerProductionBox
from production.model import ProdStates


class KeepProdStateBox(OrderChangerProductionBox):
    def __init__(self, name, sons, states, logger=None):
        super(KeepProdStateBox, self).__init__(name, sons, logger)
        states = ensure_iterable(states)
        self.allowed_states = {}
        for state in states:
            self.allowed_states[state] = state

    def change_order(self, order):
        if order.prod_state in self.allowed_states:
            order.prod_state = ProdStates.NORMAL

        return order
