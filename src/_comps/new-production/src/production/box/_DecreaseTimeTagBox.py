import operator

import iso8601

from production.model import ProductionOrder, StateEvent
from typing import Optional, List

from ._OrderChangerProductionBox import OrderChangerProductionBox


def get_time_diff_from_timestamp(first_time, last_time):
    return (iso8601.parse_date(last_time) - iso8601.parse_date(first_time)).total_seconds()


def get_state_timestamp(order, state_type, value, get_last=False):
    # type: (ProductionOrder, str, str, bool) -> Optional[str]
    if state_type.lower() == "order_state":
        order_state_history = reversed(order.state_history) if get_last else order.state_history
        for order_state in order_state_history:
            if order_state.state == value:
                return order_state.timestamp
        return None

    prod_state_history = reversed(order.prod_state_history) if get_last else order.prod_state_history
    for prod_state in prod_state_history:
        if prod_state.prod_state == value:
            return prod_state.timestamp
    return None


def _get_consolidated_state_history(order):
    # type: (ProductionOrder) -> List[StateEvent]
    return sorted(list(order.state_history) + list(order.prod_state_history), key=operator.attrgetter("timestamp"))


class DecreaseTimeTagBox(OrderChangerProductionBox):
    def __init__(self, name, sons, logger, get_config):
        super(DecreaseTimeTagBox, self).__init__(name, sons, logger)
        self.first_state_value = get_config("FirstState").get("State")
        self.first_state_type = get_config("FirstState").get("Type")
        self.last_state_value = get_config("LastState").get("State")
        self.last_state_type = get_config("LastState").get("Type")
        self.tag_name = get_config("TagName")

    def change_order(self, order):
        if self.tag_name not in order.tags:
            return order
        time_to_decrease = 0

        found_start_state = None
        found_end_state = None
        for state in _get_consolidated_state_history(order):
            if not found_start_state:
                if self.first_state_type.lower() == "order_state":
                    if state.state == self.first_state_value:
                        found_start_state = state
                else:
                    if state.prod_state == self.first_state_value:
                        found_start_state = state
            elif not found_end_state:
                if self.last_state_type.lower() == "order_state":
                    if state.state == self.last_state_value:
                        found_end_state = state
                else:
                    if state.prod_state == self.last_state_value:
                        found_end_state = state
            else:
                time_to_decrease += get_time_diff_from_timestamp(found_start_state.timestamp, found_end_state.timestamp)
                found_start_state = found_end_state = None
        order.tags[self.tag_name] -= time_to_decrease

        first_state_timestamp = get_state_timestamp(order, self.first_state_type, self.first_state_value)
        last_state_timestamp = get_state_timestamp(order, self.last_state_type, self.last_state_value, get_last=True)
        if first_state_timestamp and last_state_timestamp:
            tr_time = get_time_diff_from_timestamp(first_state_timestamp, last_state_timestamp)
            self.debug("Order TR Time {}".format(tr_time))
            order.tags[self.tag_name] = tr_time

        return order
