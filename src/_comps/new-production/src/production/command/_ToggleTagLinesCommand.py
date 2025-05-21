from ._ProductionCommand import ProductionCommand


class ToggleTagLinesCommand(ProductionCommand):
    def __init__(self, order_id, view, line_ids, tag):
        super(ToggleTagLinesCommand, self).__init__(order_id, view)
        self.line_ids = line_ids
        self.tag = tag

    def get_hash_extra_value(self):
        return "ToggleTagLinesCommand{}{}".format(self.line_ids, self.tag)
