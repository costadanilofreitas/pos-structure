from mw_helper import ensure_iterable

from production.box._OrderChangerProductionBox import OrderChangerProductionBox


class OrderProductCategoryFilterBox(OrderChangerProductionBox):
    def __init__(self, name, sons, allowed_category, forbidden_category, filter_method, logger=None):
        super(OrderProductCategoryFilterBox, self).__init__(name, sons, logger)
        self.allowed_category = ensure_iterable(allowed_category)
        self.forbidden_category = ensure_iterable(forbidden_category)
        self.filter_method = filter_method

    def change_order(self, order):
        new_order_items = []
        change = False

        allow, forbid = self.any_item_filter(order)

        if self.filter_method == "any":
            change = True

            if any(allow):
                new_order_items = order.items
            elif any(forbid):
                new_order_items = []

        if self.filter_method == "all":
            if any(allow):
                change = True
                new_order_items = order.items

            if any(forbid):
                change = True
                new_order_items = []

        if self.filter_method == "only":
            if any(allow):
                change = True
                new_order_items = [only for only in allow if only in order.items]

            if any(forbid):
                change = True
                new_order_items = filter(
                    lambda x: x not in [other for other in forbid if other in order.items],
                    order.items
                )

        if change:
            order.items = new_order_items

        return order

    def any_item_filter(self, order):
        allow_items = []
        forbid_items = []

        def alter(items, category_list, alter_list):
            for item in items:
                if item.items:
                    alter(item.items, category_list, alter_list)

                for category in category_list:
                    if category and category in item.json_tags:
                        alter_list.append(item)

        alter(order.items, self.allowed_category, allow_items)
        alter(order.items, self.forbidden_category, forbid_items)

        return allow_items, forbid_items
