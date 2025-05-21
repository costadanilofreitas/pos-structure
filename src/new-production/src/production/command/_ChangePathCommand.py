from ._ProductionCommand import ProductionCommand


class ChangePathCommand(ProductionCommand):
    def __init__(self, path, enabled):
        super(ChangePathCommand, self).__init__(None, None)
        self.path = path
        self.enabled = enabled

    def get_hash_extra_value(self):
        # type: () -> str
        return "ChangePathCommand{}{}".format(self.path, self.enabled)
