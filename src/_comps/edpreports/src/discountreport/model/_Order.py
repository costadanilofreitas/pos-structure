from datetime import datetime


class Order(object):
    def __init__(self, order_id, discount_amount, total_gross, applied_date, operator, authorizer):
        # type: (int, float, float, datetime, int, int) -> None
        self.order_id = order_id
        self.discount_amount = discount_amount
        self.total_gross = total_gross
        self.applied_date = applied_date
        self.operator = operator
        self.authorizer = authorizer
