from logging import Logger

from production.box import ProductionBox
from ._OrderCondition import OrderCondition


class ConditionBox(ProductionBox):
    def __init__(self, name, condition, true_son, false_son, logger=None):
        # type: (str, OrderCondition, ProductionBox, ProductionBox, Logger) -> None
        super(ConditionBox, self).__init__(name, [true_son, false_son], logger)
        self.condition = condition
        self.true_son = true_son
        self.false_son = false_son

    def order_modified(self, order):
        if self.condition.evaluate(order):
            self.debug("Choosing: {}", self.true_son.name)
            self.true_son.order_modified(order)
        else:
            self.debug("Choosing: {}", self.false_son.name)
            self.false_son.order_modified(order)

    def __setattr__(self, name, value):
        if name == "sons" and isinstance(value, list) and len(value) >= 2:
            self.true_son = value[0]
            self.false_son = value[1]

        super(ConditionBox, self).__setattr__(name, value)


