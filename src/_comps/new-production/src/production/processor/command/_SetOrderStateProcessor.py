from production.command import CommandType
from production.box import ViewBox
from production.model.request import ChangeProdStateRequest
from typing import List

from ._CommandProcessor import CommandProcessor


class SetOrderStateProcessor(CommandProcessor):
    def __init__(self, view_boxes):
        # type: (List[ViewBox]) -> None
        super(SetOrderStateProcessor, self).__init__(view_boxes)

    def parse_data(self, data):
        parts = data.split('\0')
        return ChangeProdStateRequest(int(parts[0]), parts[1], parts[2])

    def get_command_type(self):
        return CommandType.change_prod_state
