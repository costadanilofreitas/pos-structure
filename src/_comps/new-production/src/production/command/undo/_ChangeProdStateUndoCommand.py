from typing import List
from datetime import datetime

from ._UndoCommand import UndoCommand


class ChangeProdStateUndoCommand(UndoCommand):
    def __init__(self, order_id, view, previous_prod_state, disabled_commands):
        # type: (int, str, str, List[UndoCommand]) -> None
        super(ChangeProdStateUndoCommand, self).__init__(order_id, view)
        self.previous_prod_state = previous_prod_state
        self.disabled_commands = disabled_commands

    def undo(self, order):
        order.prod_state = self.previous_prod_state

        for undo_command in self.disabled_commands:
            undo_command.enable()
