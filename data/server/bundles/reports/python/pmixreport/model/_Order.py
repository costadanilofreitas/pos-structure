from datetime import datetime


class OrderSate(object):
    Voided = 4
    Paid = 5


class Order(object):
    def __init__(self, order_id, date, state):
        # type: (int, datetime, int) -> None
        self.order_id = order_id
        self.date = date
        self.state = state
