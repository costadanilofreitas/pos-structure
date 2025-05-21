class SaleLine(object):
    def __init__(self, seat_number, order_id, line_number, item_id, level, part_code):
        self.seat_number = seat_number
        self.order_id = order_id
        self.line_number = line_number
        self.item_id = item_id
        self.level = level
        self.part_code = part_code

    @classmethod
    def load_info(cls, seat_number, sale_line):
        cls.seat_number = seat_number
        cls.order_id = sale_line["orderId"] if "orderId" in sale_line else None
        cls.line_number = sale_line["lineNumber"] if "lineNumber" in sale_line else None
        cls.item_id = sale_line["itemId"] if "itemId" in sale_line else None
        cls.level = sale_line["level"] if "level" in sale_line else None
        cls.part_code = sale_line["partCode"] if "partCode" in sale_line else None
        return cls
