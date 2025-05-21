from mw_helper import ensure_iterable

from ._OrderCondition import OrderCondition


class PodTypeCondition(OrderCondition):
    def __init__(self, pod_types):
        self.valid_pod_types = ensure_iterable(pod_types)

    def evaluate(self, order):
        return order.pod_type in self.valid_pod_types
