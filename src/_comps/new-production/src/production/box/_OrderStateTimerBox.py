from ._OrderChangerProductionBox import OrderChangerProductionBox


class OrderStateTimerBox(OrderChangerProductionBox):

    def __init__(self, name, sons, order_state, logger=None):
        super(OrderStateTimerBox, self).__init__(name, sons, logger)
        self.order_state = order_state

    def change_order(self, order):
        for order_state in order.state_history:
            if order_state.state == self.order_state:
                order.display_time = order_state.timestamp
                return order

        return order
