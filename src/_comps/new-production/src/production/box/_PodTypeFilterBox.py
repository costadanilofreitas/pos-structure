from datetime import datetime
from mw_helper import convert_to_dict, ensure_list
from production.box._OrderChangerProductionBox import OrderChangerProductionBox
from production.model import ProdStates


class PodTypeFilterBox(OrderChangerProductionBox):
    def __init__(self, name, sons, allowed_pod_types, excluded_pod_types=None, logger=None):
        super(PodTypeFilterBox, self).__init__(name, sons, logger)
        if allowed_pod_types is None:
            allowed_pod_types = []
        self.allowed_pod_types = convert_to_dict(ensure_list(allowed_pod_types))
        if excluded_pod_types is None:
            excluded_pod_types = []
        self.excluded_pod_types = convert_to_dict(ensure_list(excluded_pod_types))

    def change_order(self, order):
        if len(self.excluded_pod_types) > 0:
            if order.pod_type in self.excluded_pod_types:
                order.prod_state = ProdStates.INVALID
                order.items = []
                return order
            else:
                return order

        if order.pod_type not in self.allowed_pod_types:
            order.prod_state = ProdStates.INVALID
            order.items = []
            return order

        return order
