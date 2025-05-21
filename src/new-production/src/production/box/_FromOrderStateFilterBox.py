from mw_helper import ensure_iterable

from production.box._OrderChangerProductionBox import OrderChangerProductionBox


class FromOrderStateFilterBox(OrderChangerProductionBox):
    def __init__(self, name, sons, states, logger=None):
        super(FromOrderStateFilterBox, self).__init__(name, sons, logger)
        self.states = ensure_iterable(states)

    def change_order(self, order):
        state_history = [x.state for x in order.state_history]
        for state in self.states:
            if state in state_history:
                return order

        return None
