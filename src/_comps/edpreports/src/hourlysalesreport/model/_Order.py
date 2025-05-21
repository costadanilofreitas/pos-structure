class Order(object):
    def __init__(self, timestamp, sale_type, amount):
        self.timestamp = timestamp
        self.sale_type = sale_type
        self.amount = amount
