from logging import Logger

from production.manager import OrderChanger
from production.view import ProductionView, KdsView
from production.box._OrderChangerProductionBox import OrderChangerProductionBox


class ItemSequencerBox(OrderChangerProductionBox):
    def __init__(self, name, order_changer, sons, logger=None):
        # type: (str, OrderChanger, ProductionView, Logger) -> None
        super(ItemSequencerBox, self).__init__(name, sons, logger)
        self.order_changer = order_changer

    def change_order(self, order):
        def set_total_items(inner_item, total_count):
            if inner_item.is_product():
                inner_item.total_count = total_count
            else:
                for son in inner_item.items:
                    set_total_items(son, total_count)

        def count_all_items(inner_item, count_item):
            if inner_item.is_product():
                count_item += inner_item.qty
                inner_item.count = count_item
                return count_item
            else:
                for son in inner_item.items:
                    count_item = count_all_items(son, count_item)

                return count_item

        count = 0
        for item in order.items:
            count = count_all_items(item, count)

        for item in order.items:
            set_total_items(item, count)

        return order
