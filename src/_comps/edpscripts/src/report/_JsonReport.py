from ._Report import Report


class JsonReport(Report):
    def __init__(self, parts, width):
        self.parts = parts
        self.width = width

    def get_parts(self):
        return self.parts

    def get_width(self):
        return self.width
