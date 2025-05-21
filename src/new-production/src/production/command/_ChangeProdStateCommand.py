from production.command import ProductionCommand


class ChangeProdStateCommand(ProductionCommand):
    def __init__(self, order_id, view, state):
        super(ChangeProdStateCommand, self).__init__(order_id, view)
        self.state = state

    def get_hash_extra_value(self):
        # type: () -> str
        return "ChangeProdStateCommand{}".format(self.state)
