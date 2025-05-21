from ._OrderChangerProductionBox import OrderChangerProductionBox


class FilterDefaultQuantityIngredientsBox(OrderChangerProductionBox):
    def __init__(self, name, sons, logger=None):
        super(FilterDefaultQuantityIngredientsBox, self).__init__(name, sons, logger)
        self.first_stored_time = None

    def change_order(self, order):
        self._remove_ingredients_with_qty_equals_default_qty(order.items)
        return order

    def _remove_ingredients_with_qty_equals_default_qty(self, items):
        for item in items[:]:
            if item.item_type == 'INGREDIENT' and item.qty == item.default_qty:
                items.remove(item)

            if item.items and len(item.items) > 0:
                self._remove_ingredients_with_qty_equals_default_qty(item.items)
