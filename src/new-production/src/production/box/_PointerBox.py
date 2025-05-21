from production.box._OrderChangerProductionBox import OrderChangerProductionBox


class PointerBox(OrderChangerProductionBox):
    def __init__(self, name, sons, points, default_points, count_merged_items, logger=None):
        super(PointerBox, self).__init__(name, sons, logger)
        self.points = points
        self.default_points = default_points
        self.count_merged_items = count_merged_items

    def change_order(self, order):
        order.points = self.add_points(order.items)
        return order

    def add_points(self, items):
        order_points = 0
        for item in items:
            if not self.count_merged_items and hasattr(item, "stamped"):
                continue
            if item.is_product():
                if item.part_code in self.points:
                    item.points = self.points[item.part_code] * item.multiplied_qty
                else:
                    item.points = self.default_points * item.multiplied_qty
                order_points += item.points
            else:
                self.add_points(item.items)
        return order_points
