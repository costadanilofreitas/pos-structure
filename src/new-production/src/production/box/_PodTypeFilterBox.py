from mw_helper import convert_to_dict, ensure_list
from production.box._OrderChangerProductionBox import OrderChangerProductionBox


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
        if self.excluded_pod_types:
            if order.pod_type in self.excluded_pod_types:
                return None

            return order

        if order.pod_type not in self.allowed_pod_types:
            return None

        return order
