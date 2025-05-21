from production.box._OrderChangerProductionBox import OrderChangerProductionBox
from production.model import ProdStates, is_product


class RemoveDoingWhenDoneBox(OrderChangerProductionBox):
    def __init__(self, name, sons, logger=None):
        super(RemoveDoingWhenDoneBox, self).__init__(name, sons, logger)
        self.tags = ["doing", "done"]

    def change_order(self, order):
        for item in order.items:
            self.remove_doing_when_done_from_item(item)

        return order

    def remove_doing_when_done_from_item(self, item):
        if item.has_tag("done") and item.has_tag("doing"):
            item.remove_tag("doing")

        for son in item.items:
            self.remove_doing_when_done_from_item(son)
