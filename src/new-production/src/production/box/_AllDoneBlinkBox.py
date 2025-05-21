from datetime import datetime

from production.box._OrderChangerProductionBox import OrderChangerProductionBox


class AllDoneBlinkBox(OrderChangerProductionBox):
    def __init__(self, name, sons, logger=None):
        super(AllDoneBlinkBox, self).__init__(name, sons, logger)
        self.done_tags = ["done", "no-cook"]

    def change_order(self, order):
        for item in order.items:
            if item.item_type == "COMBO":
                if not self.all_sons_has_tag(item.items, self.done_tags):
                    return order
            else:
                if item.voided:
                    continue

                if not any(x in item.tags for x in self.done_tags):
                    return order

        order.tagged_timestamp = datetime.now().isoformat()
        return order

    @staticmethod
    def all_sons_has_tag(sons, tags_list):
        for son in sons:
            if son.voided:
                continue

            product_tags = son.get_tags()
            product_has_tags = False

            for tag in tags_list:
                if tag in product_tags:
                    product_has_tags = True
                    break

            if not product_has_tags:
                return False

        return True
