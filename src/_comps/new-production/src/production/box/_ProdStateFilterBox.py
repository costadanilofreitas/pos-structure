from datetime import datetime
from mw_helper import ensure_list, convert_to_dict
from production.box._OrderChangerProductionBox import OrderChangerProductionBox


class ProdStateFilterBox(OrderChangerProductionBox):
    def __init__(self, name, sons, allowed_prod_states, excluded_prod_states, logger=None):
        super(ProdStateFilterBox, self).__init__(name, sons, logger)
        self.allowed_prod_states = convert_to_dict(ensure_list(allowed_prod_states))
        self.excluded_prod_states = convert_to_dict(ensure_list(excluded_prod_states))

    def change_order(self, order):
        if self.should_filter_order(order):
            order.items = []
            order.prod_state = 'INVALID'
            return order

        return order

    def should_filter_order(self, order):
        if self.allowed_prod_states and order.prod_state not in self.allowed_prod_states:
            return True
        if self.excluded_prod_states and order.prod_state in self.excluded_prod_states:
            return True
        return False
