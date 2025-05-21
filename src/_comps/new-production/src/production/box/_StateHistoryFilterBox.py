from datetime import datetime
from mw_helper import ensure_iterable, convert_to_dict
from production.box._OrderChangerProductionBox import OrderChangerProductionBox
from production.model import ProdStates, StateEvent


class StateHistoryFilterBox(OrderChangerProductionBox):
    def __init__(self, name, sons, order_states, logger=None):
        super(StateHistoryFilterBox, self).__init__(name, sons, logger)
        self.allowed_states = convert_to_dict(ensure_iterable(order_states))

    def change_order(self, order):
        passed_through_state = False
        for history in order.state_history:  # type: StateEvent
            if history.state in self.allowed_states:
                passed_through_state = True
                break

        if not passed_through_state:
            order.items = []
            order.prod_state = ProdStates.INVALID
            return order

        return order
