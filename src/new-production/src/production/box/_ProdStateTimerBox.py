from ._OrderChangerProductionBox import OrderChangerProductionBox


class ProdStateTimerBox(OrderChangerProductionBox):

    def __init__(self, name, sons, prod_state, logger=None):
        super(ProdStateTimerBox, self).__init__(name, sons, logger)
        self.prod_state = prod_state

    def change_order(self, order):
        order_timestamp = self.get_order_timestamp_by_prod_state(order)
        if order_timestamp:
            order.display_time = order_timestamp

        return order

    def get_order_timestamp_by_prod_state(self, order):
        for state in reversed(order.prod_state_history):
            if state.prod_state == self.prod_state:
                return state.timestamp
        return None


