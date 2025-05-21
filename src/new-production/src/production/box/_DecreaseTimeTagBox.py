import operator

import iso8601

from production.model import ProductionOrder, StateEvent
from typing import Optional, List

from ._OrderChangerProductionBox import OrderChangerProductionBox


def get_time_diff_from_timestamp(first_time, last_time):
    return (iso8601.parse_date(last_time) - iso8601.parse_date(first_time)).total_seconds()


def _get_consolidated_state_history(order):
    # type: (ProductionOrder) -> List[StateEvent]
    consolidated_state_history = []
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
                found_start_state = self._check_found_state(state, self.first_state_type, self.first_state_value)

            elif not found_end_state:
                found_end_state = self._check_found_state(state, self.last_state_type, self.last_state_value)

            else:
                time_to_decrease += get_time_diff_from_timestamp(found_start_state.timestamp, found_end_state.timestamp)
                found_start_state = found_end_state = None

        order.tags[self.tag_name] -= time_to_decrease

        return order

    def _check_found_state(self, state, state_type, state_value):
        found_state = None
        if state_type.lower() == "order_state":
            if state.state == state_value:
                found_state = state

        elif state.prod_state == state_value:
            found_state = state

        return found_state
