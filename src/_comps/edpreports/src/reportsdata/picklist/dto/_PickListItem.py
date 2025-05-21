class PickListItem(object):
    def __init__(self, item):
        self.sub_items = []

        qty, default_qty, item_type, description, multiplied_qty = map(item.get, ("qty",
                                                                                  "default_qty",
                                                                                  "item_type",
                                                                                  "description",
                                                                                  "multiplied_qty"))

        self.qty = qty
        self.default_qty = default_qty
        self.multiplied_qty = multiplied_qty
        self.item_type = item_type
        self.description = description

        items = item.findall("Item")
        for item in items:
            self.sub_items.append(PickListItem(item))
