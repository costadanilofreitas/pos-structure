from ._OrderChangerProductionBox import OrderChangerProductionBox
from production.model import ProdStates


class ComboServedWhenAllServedBox(OrderChangerProductionBox):
    def __init__(self, name, sons, logger=None):
        super(ComboServedWhenAllServedBox, self).__init__(name, sons, logger)

    def change_order(self, order):
        for item in order.items:
            if item.item_type == "COMBO" and self.check_sons_tags(item.items, ["served", "no-cook"]):
                item.add_tag("served")
                order.prod_state = ProdStates.SERVED

        return order

    @staticmethod
    def check_sons_tags(sons, tags_list):
        for son in sons:
            if not son.all_has_at_least_one_tag(tags_list):
                return False
        return True

