from logging import Logger

from production.manager import OrderChanger
from production.view import ProductionView
from production.box._OrderChangerProductionBox import OrderChangerProductionBox


class StampItemsViewBox(OrderChangerProductionBox):
    def __init__(self, name, order_changer, view, sons, logger=None):
        # type: (str, OrderChanger, ProductionView, str, Logger) -> None
        super(StampItemsViewBox, self).__init__(name, sons, logger)
        self.order_changer = order_changer
        self.view = view

    def change_order(self, order):
        def stamp_item(item_to_change):
            return item_to_change.add_view(self.view.view_name)

        self.order_changer.change_items(order, stamp_item)

        return order
