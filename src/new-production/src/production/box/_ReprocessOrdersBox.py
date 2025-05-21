from production.model import ProdStates, ProductionOrder

from ._OrderChangerProductionBox import OrderChangerProductionBox


class ReprocessOrdersBox(OrderChangerProductionBox):
    def __init__(self, name, sons, publish_scheduler, reprocess_time, logger=None):
        super(ReprocessOrdersBox, self).__init__(name, sons, logger)
        self.publish_scheduler = publish_scheduler
        self.reprocess_time = reprocess_time

    def change_order(self, order):
        # type: (ProductionOrder) -> ProductionOrder

        self.publish_scheduler.remove_schedule_publish(order.order_id)
        if order.prod_state != ProdStates.INVALID:
            self.publish_scheduler.schedule_publish(order.order_id, self.reprocess_time)

        return order
