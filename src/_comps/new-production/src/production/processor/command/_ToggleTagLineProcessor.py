from production.command import CommandType
from production.box import ViewBox
from production.model.request import ToggleTagLineRequest, SaleLine
from typing import List

from ._CommandProcessor import CommandProcessor


class ToggleTagLineProcessor(CommandProcessor):
    def __init__(self, view_boxes):
        # type: (List[ViewBox]) -> None
        super(ToggleTagLineProcessor, self).__init__(view_boxes)

    def parse_data(self, data):
        parts = data.split('\0')
        lines = parts[2].split(";")
        sale_lines = []
        for line in lines:
            line_parts = line.split('-')
            sale_lines.append(SaleLine(line_parts[0], line_parts[1], line_parts[2], line_parts[3]))
        return ToggleTagLineRequest(int(parts[0]),
                                    parts[1],
                                    sale_lines,
                                    parts[3])

    def get_command_type(self):
        return CommandType.toggle_tag_line
