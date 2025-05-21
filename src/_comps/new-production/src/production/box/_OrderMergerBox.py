from datetime import datetime
from production.box._OrderChangerProductionBox import OrderChangerProductionBox
from production.model import ProdStates


class OrderMergerBox(OrderChangerProductionBox):
    def __init__(self, name, sons, logger=None):
        super(OrderMergerBox, self).__init__(name, sons, logger)

    def change_order(self, order):
        stored_order = self.get_order(order.order_id)
        if stored_order and hasattr(order, "stamped"):
            order.items = self._get_stamped_items(stored_order, order)
            order.stamped = True
            order.prod_state = self._get_new_order_state(order, stored_order)

        if order.prod_state in (ProdStates.SERVED, ProdStates.INVALID) and not order.items:
            self.delete_order(order.order_id)
        else:
            self.save_order(order)
        return order

    @staticmethod
    def _get_new_order_state(order, stored_order):
        all_states = [x.prod_state for x in [order, stored_order]]
        state_values = {"": 4,
                        None: 4,
                        ProdStates.NORMAL: 3,
                        ProdStates.SERVED: 2,
                        ProdStates.INVALID: 1}
        state_weights = []
        for state in all_states:
            if state in state_values:
                state_weights.append(state_values[state])

        if not state_weights:
            return order.prod_state

        return next((state for state, weight in state_values.items() if weight == max(state_weights)))

    def _get_stamped_items(self, stored_order, order):
        stamped_items = stored_order.items
        stamped_order_item_codes = self._list_order_item_codes(stored_order)
        for item in order.items:
            if hasattr(item, "stamped") and item.item_code not in stamped_order_item_codes:
                stamped_items.append(item)
        return stamped_items

    @staticmethod
    def _list_order_item_codes(order):
        item_ids = {}
        for item in order.items:
            item_ids[item.item_code] = ""
        return item_ids
