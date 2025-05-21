from datetime import datetime
from mw_helper import ensure_iterable, convert_to_dict
from production.box._OrderChangerProductionBox import OrderChangerProductionBox
from production.model import ProdStates


class CustomPropertyFilterBox(OrderChangerProductionBox):
    def __init__(self, name, sons, allowed_properties, forbidden_properties=None, logger=None):
        super(CustomPropertyFilterBox, self).__init__(name, sons, logger)
        if allowed_properties is None:
            self.allowed_properties = []
        else:
            self.allowed_properties = ensure_iterable(allowed_properties)
        if forbidden_properties is None:
            self.forbidden_properties = []
        else:
            self.forbidden_properties = ensure_iterable(forbidden_properties)

    def change_order(self, order):
        if len(self.forbidden_properties) > 0:
            for prop in self.forbidden_properties:
                if prop in order.properties:
                    order.items = []
                    order.prod_state = ProdStates.INVALID
                    break

        if len(self.allowed_properties) > 0:
            if all(allowed_prop not in order.properties for allowed_prop in self.allowed_properties):
                order.items = []
                order.prod_state = ProdStates.INVALID

        return order
