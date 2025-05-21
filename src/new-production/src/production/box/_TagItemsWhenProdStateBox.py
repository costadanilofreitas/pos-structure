from ._OrderChangerProductionBox import OrderChangerProductionBox


class TagItemsWhenProdStateBox(OrderChangerProductionBox):
    def __init__(self, name, sons, prod_state, tag, logger=None):
        super(TagItemsWhenProdStateBox, self).__init__(name, sons, logger)
        self.prod_state = prod_state
        self.tag = tag

    def change_order(self, order):
        if order.prod_state == self.prod_state:
            self._tag_items(order.items)

        return order

    def _tag_items(self, items):
        for item in items:
            item.add_tag(self.tag)
            
            if item.items:
                self._tag_items(item.items)
