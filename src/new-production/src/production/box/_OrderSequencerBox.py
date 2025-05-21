from abc import ABCMeta, abstractmethod
from datetime import timedelta
from logging import Logger

import iso8601
from mw_helper import ensure_iterable, ensure_list
from production.box import ProductionBox
from production.box._OrderChangerProductionBox import OrderChangerProductionBox
from production.model import all_done, ProductionOrder, TagEventType
from typing import Optional, Union, List


def _get_order_display_time(order):
    display_time = order.display_time
    if display_time == "":
        display_time = order.created_at
    return display_time


class OrderSequencerBox(OrderChangerProductionBox):
    def __init__(self, name, sons, sorters, logger=None):
        # type: (str, Optional[Union[List[ProductionBox]], ProductionBox], Optional[Union[List[OrderSorter]]], Logger) -> None # noqa
        super(OrderSequencerBox, self).__init__(name, sons, logger)
        self.sorters = ensure_iterable(sorters)  # type: List[OrderSequencerBox.OrderSorter]

    def change_order(self, order):
        sequence = ""
        for sorter in self.sorters:
            sequence += sorter.create_prod_sequence(order)

        order.prod_sequence = sequence
        return order

    class OrderSorter(object):
        __metaclass__ = ABCMeta

        @abstractmethod
        def create_prod_sequence(self, order):
            # type: (ProductionOrder) -> str
            raise NotImplementedError()

    class PriorityCustomerSorter(OrderSorter):
        def create_prod_sequence(self, order):
            if "PRIORITY" in order.properties and order.properties["PRIORITY"] == "true":
                return "00"
            for item in order.items:
                if 'highPriority' in item.properties:
                    return "10"
            return "99"

    class PodTypeSorter(OrderSorter):
        def __init__(self, pod_type_order):
            # type: (Optional[Union[List[str], str]]) -> None
            self.pod_type_order = ensure_list(pod_type_order)

        def create_prod_sequence(self, order):
            try:
                index = self.pod_type_order.index(order.pod_type)
                return str(index).zfill(2)
            except ValueError:
                return "99"

    class DoneInFrontSorter(OrderSorter):
        def create_prod_sequence(self, order):
            if all_done(order):
                return "00"
            else:
                return "99"

    class SaleTypeSorter(OrderSorter):
        def __init__(self, sale_type_order):
            self.sale_type_order = ensure_list(sale_type_order)

        def create_prod_sequence(self, order):
            try:
                index = self.sale_type_order.index(order.sale_type)
                return str(index).zfill(2)
            except ValueError:
                return "99"

    class OrderIdSorter(OrderSorter):
        def create_prod_sequence(self, order):
            return str(order.order_id)

    class OrderStateSorter(OrderSorter):
        def __init__(self, state_order):
            self.state_order = ensure_list(state_order)

        def create_prod_sequence(self, order):
            try:
                index = self.state_order.index(order.state)
                return str(index).zfill(2)
            except ValueError:
                return "99"

    class LastModifiedSorter(OrderSorter):
        def __init__(self, last_modified_first=False):
            super(OrderSequencerBox.LastModifiedSorter, self).__init__()
            self.last_modified_first = last_modified_first

        def create_prod_sequence(self, order):
            if self.last_modified_first:
                future_date = iso8601.parse_date("3000-02-13T00:00:00Z")
                past_date = iso8601.parse_date("1984-02-13T00:00:00Z")
                last_change_date = iso8601.parse_date(order.state_history[-1].timestamp)
                return past_date + timedelta(seconds=(future_date - last_change_date).total_seconds())
            else:
                return order.state_history[-1].timestamp

    class DisplayTimeSorter(OrderSorter):
        def __init__(self, invert=True):
            self.invert = invert

        def create_prod_sequence(self, order):
            display_time = _get_order_display_time(order)

            if display_time and self.invert:
                future_date = iso8601.parse_date("3000-02-13T00:00:00Z")
                past_date = iso8601.parse_date("1984-02-13T00:00:00Z")
                last_change_date = iso8601.parse_date(display_time)
                return (past_date + timedelta(seconds=(future_date - last_change_date).total_seconds())).strftime("%Y%m%d%H%M%S")

            return display_time

    class DoneSorter(OrderSorter):
        def create_prod_sequence(self, order):
            last_done = None
            if not all_done(order):
                return ""

            for item in order.items:
                for event in reversed(item.tag_history):
                    if event.tag == 'done' and event.action == TagEventType.added:
                        if last_done is None or last_done < event.date:
                            last_done = event.date
                        break

            if last_done is not None:
                return last_done.isoformat()

            return _get_order_display_time(order)
