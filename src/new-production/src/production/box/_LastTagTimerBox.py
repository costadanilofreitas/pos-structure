from production.model import TagEventType

from ._OrderChangerProductionBox import OrderChangerProductionBox


class LastTagTimerBox(OrderChangerProductionBox):

    def __init__(self, name, sons, tag, logger=None):
        super(LastTagTimerBox, self).__init__(name, sons, logger)
        self.tag = tag

    def change_order(self, order):
        last_timestamp = self.get_last_timestamp(order)
        if last_timestamp is not None:
            order.display_time = last_timestamp
        return order

    def get_last_timestamp(self, order):
        for item in order.items:
            if item.has_tag(self.tag):
                for history in item.tag_history:
                    if history.tag == self.tag and history.action == TagEventType.added:
                        return history.date.isoformat()

        return None
