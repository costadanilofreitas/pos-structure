from mw_helper import ensure_iterable

from ._OrderCondition import OrderCondition


class CustomPropertyCondition(OrderCondition):
    def __init__(self, properties):
        self.properties = ensure_iterable(properties)

    def evaluate(self, order):
        for prop in self.properties:
            if prop in order.properties:
                return True

        return False
