import iso8601

from ._OrderChangerProductionBox import OrderChangerProductionBox
from mw_helper import convert_from_localtime_to_utc


class FilterDeletedItemsBeforeFirstStateBox(OrderChangerProductionBox):
    def __init__(self, name, sons, order_state, logger=None):
        super(FilterDeletedItemsBeforeFirstStateBox, self).__init__(name, sons, logger)
        self.order_state = order_state
        self.first_stored_time = None

    def change_order(self, order):
        self.first_stored_time = self._get_first_state_time(order)

        if self.first_stored_time is None:
            return order

        self._remove_empty_items(order.items)

        return order

    def _get_first_state_time(self, order):
        stored_states = [state for state in order.state_history if state.state == self.order_state]
        if len(stored_states) > 0:
            return convert_from_localtime_to_utc(iso8601.parse_date(stored_states[0].timestamp)).isoformat()

        return None

    def _remove_empty_items(self, items):
        for item in items[:]:
            item_is_not_ingredient_or_option = item.item_type != 'INGREDIENT' and item.item_type != 'OPTION'
            if item.qty == 0 and item.last_updated < self.first_stored_time and item_is_not_ingredient_or_option:
                items.remove(item)

            if item.items and len(item.items) > 0:
                self._remove_empty_items(item.items)

