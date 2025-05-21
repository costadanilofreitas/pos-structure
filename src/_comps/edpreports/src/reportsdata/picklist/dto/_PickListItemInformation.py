class PickListItemInformation(object):
    def __init__(self, qty, default_qty, item_type, name, label, only_flag, min_qty):
        self.qty = qty
        self.default_qty = default_qty
        self.item_type = item_type
        self.name = name
        self.label = label
        self.only_flag = only_flag
        self.min_qty = min_qty
