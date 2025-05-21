from production.box._OrderChangerProductionBox import OrderChangerProductionBox


class CFHHiderBox(OrderChangerProductionBox):
    def __init__(self, name, sons, cfh_items, logger=None):
        super(CFHHiderBox, self).__init__(name, sons, logger)
        self.cfh_items = cfh_items

    def change_order(self, order):
        order.items = self._find_and_remove_cfh_items(order.items[:])
        return order

    def _find_and_remove_cfh_items(self, items):
        new_items = []
        for item in items:
            if item.part_code in self.cfh_items:
                for son in item.items:
                    new_items.extend(self._find_and_remove_cfh_items([son]))
            else:
                item.items = self._find_and_remove_cfh_items(item.items)
                new_items.append(item)

        return new_items
