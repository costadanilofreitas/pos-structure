from datetime import datetime
from mw_helper import ensure_iterable
from production.box._OrderChangerProductionBox import OrderChangerProductionBox
from production.model import ProdStates, ProductionOrder


class CustomPropertyValueFilterBox(OrderChangerProductionBox):
    def __init__(self, name, sons, parameter_name, allowed_values, excluded_values=None, logger=None):
        super(CustomPropertyValueFilterBox, self).__init__(name, sons, logger)
        self.parameter_name = parameter_name
        self.allowed_values = ensure_iterable(allowed_values or [])
        self.excluded_values = ensure_iterable(excluded_values or [])

    def change_order(self, order):
        if self.should_filter_order(order):
            order.items = []
            order.prod_state = ProdStates.INVALID
        return order

    def should_filter_order(self, order):
        # type: (ProductionOrder) -> bool
        self.debug("should filter order, parameter = '{}'".format(self.parameter_name))
        if self.parameter_name in order.properties:
            prop_value = order.properties[self.parameter_name]
            self.debug("parameter value = '{}'".format(prop_value))
            self.debug("allowed values = '{}', excluded values = '{}'".format(self.allowed_values, self.excluded_values))
            if self.allowed_values and prop_value not in self.allowed_values:
                return True
            if self.excluded_values and prop_value in self.excluded_values:
                return True
        return False

