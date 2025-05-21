from mw_helper import ensure_iterable
from production.box._OrderChangerProductionBox import OrderChangerProductionBox
from production.model import ProdStates


class SaleTypeFilterBox(OrderChangerProductionBox):
    def __init__(self, name, sons, sale_types, logger=None):
        super(SaleTypeFilterBox, self).__init__(name, sons, logger)
        sale_types = ensure_iterable(sale_types)

        self.allowed_sale_types = {}
        for sale_type in sale_types:
            self.allowed_sale_types[sale_type] = sale_type

    def change_order(self, order):
        if order.sale_type not in self.allowed_sale_types:
            order.prod_state = ProdStates.INVALID

        return order
