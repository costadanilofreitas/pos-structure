from datetime import datetime

from production.box._OrderChangerProductionBox import OrderChangerProductionBox
from production.model import ProdStates


class DisplayTimeFilterBox(OrderChangerProductionBox):
    def __init__(self, name, sons, expiration_time, logger=None):
        super(DisplayTimeFilterBox, self).__init__(name, sons, logger)
        self.expiration_time = int(expiration_time)

    def change_order(self, order):
        if self.should_filter_order(order):
            order.prod_state = ProdStates.INVALID

        return order

    def should_filter_order(self, order):
        if not order.display_time:
            return False

        display_time = datetime.strptime(order.display_time[0:19], "%Y-%m-%dT%H:%M:%S")
        current_time = datetime.now()
        return (current_time - display_time).total_seconds() >= self.expiration_time
