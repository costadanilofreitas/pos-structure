from production.box._OrderChangerProductionBox import OrderChangerProductionBox


class KeepProdStateBox(OrderChangerProductionBox):
    def __init__(self, name, sons, states, logger=None):
        super(KeepProdStateBox, self).__init__(name, sons, logger)
        self.allowed_states = {}
        for state in states:
            self.allowed_states[state] = state

    def change_order(self, order):
        order.tagged_lines = ""
        return order
