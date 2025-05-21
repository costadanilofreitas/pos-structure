from typing import Union


class TableOrderSaleLine(object):

    def __init__(self, product_name, price, qty, default_qty, item_type, seat, level, comment, line_number):
        # type: (str, float, float, Union[int, None], str,  Union[int, None], int, Union[str, None], int) -> None
        self.product_name = product_name
        self.price = price
        self.qty = qty
        self.default_qty = default_qty
        self.item_type = item_type
        self.seat = seat
        self.level = level
        self.comment = comment
        self.line_number = line_number
