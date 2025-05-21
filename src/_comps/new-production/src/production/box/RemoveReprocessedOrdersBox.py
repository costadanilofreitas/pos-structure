from datetime import datetime, timedelta

from production.box._OrderChangerProductionBox import OrderChangerProductionBox
from production.model import ProdStates


class RemoveReprocessedOrdersBox(OrderChangerProductionBox):
    def __init__(self, name, sons, reprocessed_time_limit, logger=None):
        super(RemoveReprocessedOrdersBox, self).__init__(name, sons, logger)
        self.reprocessed_time_limit = int(reprocessed_time_limit)
        self.logger = logger

    def change_order(self, order):
        if order.first_processing:
            order_creation_time = datetime.strptime(order.created_at, "%Y-%m-%dT%H:%M:%S.%f")
            if (datetime.now() - order_creation_time) > timedelta(seconds=self.reprocessed_time_limit):
                self.logger.error("Order removed after reprocessing time limit. Order: \n{}".format(str(order)))

                order.prod_state = ProdStates.INVALID
                order.items = []
        return order
