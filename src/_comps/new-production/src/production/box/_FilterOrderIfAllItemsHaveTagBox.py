from ._OrderChangerProductionBox import OrderChangerProductionBox


class FilterOrderIfAllItemsHaveTagBox(OrderChangerProductionBox):
    def __init__(self, name, sons, tag, logger=None):
        super(FilterOrderIfAllItemsHaveTagBox, self).__init__(name, sons, logger)
        self.tag = tag

    def change_order(self, order):
        for item in order.items:
            if self.tag and self.tag not in item.get_tags():
                return order

        order.items = []
        return order
