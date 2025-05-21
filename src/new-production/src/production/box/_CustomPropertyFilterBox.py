from mw_helper import ensure_iterable
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
        if self.forbidden_properties:
            for prop in self.forbidden_properties:
                if prop in order.properties:
                    order.prod_state = ProdStates.INVALID
                    break

        if self.allowed_properties and self._no_allowed_properties_on_order(order):
            order.prod_state = ProdStates.INVALID

        return order

    def _no_allowed_properties_on_order(self, order):
        return all(allowed_prop not in order.properties for allowed_prop in self.allowed_properties)
