from datetime import datetime
from mw_helper import ensure_iterable, convert_to_dict
from production.box._OrderChangerProductionBox import OrderChangerProductionBox
from production.model import ProdStates


class OrderSubTypeFilterBox(OrderChangerProductionBox):
    def __init__(self, name, sons, allowed_subtypes, forbidden_subtypes, logger=None):
        super(OrderSubTypeFilterBox, self).__init__(name, sons, logger)
        self.allowed_subtypes = None
        if allowed_subtypes is not None:
            self.allowed_subtypes = convert_to_dict(ensure_iterable(allowed_subtypes))
        self.forbidden_subtypes = None
        if forbidden_subtypes is not None:
            self.forbidden_subtypes = convert_to_dict(ensure_iterable(forbidden_subtypes))

    def change_order(self, order):
        if self.forbidden_subtypes is not None and order.order_subtype in self.forbidden_subtypes:
            order.items = []
            order.prod_state = ProdStates.INVALID
            return order

        if self.allowed_subtypes is not None and order.order_subtype not in self.allowed_subtypes:
            order.items = []
            order.prod_state = ProdStates.INVALID
            return order

        return order
