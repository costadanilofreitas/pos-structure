from datetime import datetime
from typing import Union


class Order(object):
    def __init__(self, order_id, void_reason, operator_id, authorizer_id, order_datetime, total_gross):
        # type: (int, unicode, int, Union[int, None], datetime, float) -> None
        self.id = order_id
        self.reason = void_reason
        self.operator = operator_id
        self.authorizer = authorizer_id
        self.datetime = order_datetime
        self.total = total_gross
