from typing import List


class Line(object):
    def __init__(self, line_number, item_id, part_code, quantity, lines=None):
        # type: (int, str, int, int, List[Line]) -> None
        self.line_number = line_number
        self.item_id = item_id
        self.part_code = part_code
        self.quantity = quantity
        self.lines = lines if lines is not None else []

    def get_line_code(self):
        return self.item_id + "." + str(self.part_code)
