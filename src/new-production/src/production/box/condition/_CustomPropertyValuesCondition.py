from mw_helper import ensure_iterable

from ._OrderCondition import OrderCondition


class CustomPropertyValuesCondition(OrderCondition):
    def __init__(self, custom_property, allowed_values, excluded_values):
        self.custom_property = custom_property
        self.allowed_values = ensure_iterable(allowed_values or [])
        self.excluded_values = ensure_iterable(excluded_values or [])

    def evaluate(self, order):
        if self.custom_property in order.properties:
            property_value = order.properties[self.custom_property]
            if self.allowed_values and property_value in self.allowed_values:
                return True
            if self.excluded_values and property_value not in self.excluded_values:
                return True
        return False
