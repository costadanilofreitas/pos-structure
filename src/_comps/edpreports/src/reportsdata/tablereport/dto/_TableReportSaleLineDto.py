from typing import Union


class TableReportSaleLineDto(object):

    def __init__(self):
        self.product_name = ""  # type: str
        self.price = 0.0        # type: float
        self.qty = 0            # type: float
        self.default_qty = 0    # type: Union[int, None]
        self.item_type = ""     # type: str
        self.seat = None        # type: Union[int, None]
        self.level = 0          # type: int
        self.comment = ""       # type: Union[str, None]
        self.line_number = 0    # type: int
