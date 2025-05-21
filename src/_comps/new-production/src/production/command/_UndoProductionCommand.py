from production.command import ProductionCommand


class UndoProductionCommand(ProductionCommand):
    def __init__(self, view):
        super(UndoProductionCommand, self).__init__(None, view)

    def get_hash_extra_value(self):
        return "UndoProductionCommand"

