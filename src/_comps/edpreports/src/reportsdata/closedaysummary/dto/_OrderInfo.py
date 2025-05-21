class OrderInfo(object):
    def __init__(self, paid_orders, voided_orders, liquid_sales):
        self.paid_orders = paid_orders
        self.voided_orders = voided_orders
        self.liquid_sales = liquid_sales
