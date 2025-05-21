from production.command import ChangeProdStateCommand
from production.view import ProductionView


class CommandView(ProductionView):
    def __init__(self, name, command_processor, command, logger):
        super(CommandView, self).__init__(name, logger)

        self.command_processor = command_processor
        self.command = command

    def handle_order(self, order):
        production_command = ChangeProdStateCommand(order.order_id, None, self.command)
        self.command_processor.handle_command(production_command)

    def get_view_tags(self):
        return []
