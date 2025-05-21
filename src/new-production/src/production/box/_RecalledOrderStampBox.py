from production.box._OrderChangerProductionBox import OrderChangerProductionBox
from production.model import ProdStates, TagEventType


def _was_served(order):
    return any(s.prod_state in (ProdStates.SERVED, ProdStates.DELIVERED) for s in order.prod_state_history)


def _is_not_served(order):
    return order.prod_state not in (ProdStates.SERVED, ProdStates.DELIVERED)


class RecalledOrderStampBox(OrderChangerProductionBox):
    def __init__(self, name, sons, filter_tag='done', logger=None):
        super(RecalledOrderStampBox, self).__init__(name, sons, logger)
        self.filter_tag = filter_tag

    def check_item_recalled(self, order, item):
        self.logger.info("Item: {}".format(item))
        if item.qty == 0 and self.filter_tag in item.tags:
            return None
        for tag_event in item.tag_history:
            if tag_event.tag in self.filter_tag and tag_event.action == TagEventType.removed:
                self.logger.info("Order marked with recalled state: {}".format(order.order_id))
                order.prod_state = ProdStates.NORMAL
                order.recalled = True
                return order

        for sub_item in item.items:
            ret = self.check_item_recalled(order, sub_item)
            if ret is not None:
                return order

        if _is_not_served(order) and _was_served(order):
            order.recalled = True
            return order

    def change_order(self, order):
        for item in order.items:
            ret = self.check_item_recalled(order, item)
            if ret is not None:
                return order
        return order
