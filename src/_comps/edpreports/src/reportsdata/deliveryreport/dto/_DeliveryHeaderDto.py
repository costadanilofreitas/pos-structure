from datetime import datetime


class DeliveryHeaderDto(object):
    def __init__(self, order):
        # type: (unicode, unicode, int, unicode) -> ()
        self.store_name = order.store_name
        self.order_number = order.order_number
        self.order_date = datetime.strptime(order.order_date, "%Y-%m-%dT%H:%M:%S.%fZ")
