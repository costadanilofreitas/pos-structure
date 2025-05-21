from logging import Logger
from production.box import ProductionBox
from typing import List, Union, Any

from ._OrderChangerProductionBox import OrderChangerProductionBox


class SkipCourseBox(OrderChangerProductionBox):
    def __init__(self, name, sons, skip_pod_types, skip_sale_types, logger=None):
        # type: (str, Union[ProductionBox, List[ProductionBox]], List[str], List[str], Logger) -> None  # noqa
        super(SkipCourseBox, self).__init__(name, sons, logger)
        self.skip_pod_types = skip_pod_types
        self.skip_sale_types = skip_sale_types

    def change_order(self, order):
        order.skip_course = self.set_skip_course(order)
        return order

    def set_skip_course(self, order):
        return self.skip_course_by_pod_type(order) or self.skip_course_by_sale_type(order)

    def skip_course_by_pod_type(self, order):
        return order.pod_type in self.skip_pod_types

    def skip_course_by_sale_type(self, order):
        return order.sale_type in self.skip_sale_types
