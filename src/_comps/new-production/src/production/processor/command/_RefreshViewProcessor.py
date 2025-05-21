from production.command import CommandType
from production.box import ViewBox
from production.model.request import RefreshViewRequest
from typing import List

from ._CommandProcessor import CommandProcessor


class RefreshViewProcessor(CommandProcessor):
    def __init__(self, view_boxes):
        # type: (List[ViewBox]) -> None
        super(RefreshViewProcessor, self).__init__(view_boxes)

    def parse_data(self, data):
        return RefreshViewRequest(data.split('\0')[0])

    def get_command_type(self):
        return CommandType.refresh_view
