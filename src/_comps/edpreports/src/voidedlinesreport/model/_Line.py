import datetime

from typing import Optional, Union


class Line(object):
    def __init__(self,
                 order_id,
                 operator,
                 authorizator,
                 line_number,
                 quantity,
                 part_code,
                 price_key,
                 void_datetime,
                 price=None,
                 operator_name=""):
        # type: (int, int, Union[int, None], int, int, int, int, datetime, Optional[float], Optional[str]) -> None
        self.order_id = order_id
        self.operator = operator
        self.authorizator = authorizator
        self.line_number = line_number
        self.quantity = quantity
        self.part_code = part_code
        self.price_key = price_key
        self.void_datetime = void_datetime
        self.price = price
        self.operator_name = operator_name
