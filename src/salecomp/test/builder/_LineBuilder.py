from salecomp.model import Line


class LineBuilder(object):
    def __init__(self):
        self.line_number = 0
        self.item_id = "1"
        self.part_code = 0
        self.quantity = 1
        self.lines = []

    def with_line_number(self, line_number):
        self.line_number = line_number
        return self

    def with_item_id(self, item_id):
        self.item_id = item_id
        return self

    def with_part_code(self, part_code):
        self.part_code = part_code
        return self

    def with_quantity(self, quantity):
        self.quantity = quantity
        return self

    def add_line(self, line):
        self.lines.append(line)
        return self

    def build(self):
        lines = []
        for line in self.lines:
            lines.append(line.build())
        return Line(self.line_number, self.item_id, self.part_code, self.quantity, lines)