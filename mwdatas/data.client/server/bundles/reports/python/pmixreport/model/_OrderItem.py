class OrderItem(object):
    def __init__(self, name, quantity, pcode, unit_price):
        # type: (unicode, int, int, float) -> None
        self.name = name
        self.quantity = quantity
        self.pcode = pcode
        self.unit_price = unit_price
