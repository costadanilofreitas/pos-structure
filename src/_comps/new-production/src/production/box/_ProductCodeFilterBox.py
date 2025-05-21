from mw_helper import ensure_iterable

from production.box._OrderChangerProductionBox import OrderChangerProductionBox
from production.model import ProdStates


class ProductCodeFilterBox(OrderChangerProductionBox):
    def __init__(self, name, sons, product_codes, keep_children=False, logger=None):
        super(ProductCodeFilterBox, self).__init__(name, sons, logger)
        self.product_codes = ensure_iterable(product_codes)
        self.keep_children = keep_children

    def change_order(self, order):
        new_order_items = []

        def verify(product):
            return unicode(product.part_code) not in self.product_codes

        for item in order.items:
            if verify(item):
                new_order_items.append(item)

                if len(item.items) > 0:
                    self.change_order(item)
            else:
                if str(self.keep_children).lower() == "true" and len(item.items):
                    [new_order_items.append(prod) for prod in item.items if verify(prod)]

        if not len(new_order_items):
            order.prod_state = ProdStates.INVALID

        order.items = new_order_items
        return order
