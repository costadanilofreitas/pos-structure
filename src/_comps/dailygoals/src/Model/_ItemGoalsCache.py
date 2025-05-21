class ItemGoalsCache(object):
    def __init__(self, start_date, end_date, name, part_codes, quantity, operator_qty):
        self.start_date = start_date
        self.end_date = end_date
        self.name = name
        self.part_codes = part_codes
        self.quantity = quantity
        self.operator_qty = operator_qty
