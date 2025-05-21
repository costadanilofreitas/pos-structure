from typing import List

from ._TagLinesUndoCommandType import TagLinesUndoCommandType
from ._UndoCommand import UndoCommand


class TagLinesUndoCommand(UndoCommand):
    def __init__(self, order_id, view, tag, lines, type, disabled_commands):
        # type: (int, str, str, List[str], TagLinesUndoCommandType, List[UndoCommand]) -> None
        super(TagLinesUndoCommand, self).__init__(order_id, view)
        self.tag = tag
        self.lines = lines
        self.type = type
        self.disabled_commands = disabled_commands

    def undo(self, order):
        for line_id in self.lines:
            if self.type == TagLinesUndoCommandType.add:
                order.remove_tag(line_id, self.tag)
                if self.tag == 'served':
                    item = order.get_item_by_line_id(line_id)
                    if item is not None and item.has_tag("printed"):
                        item.remove_tag("printed")
                        self.remove_sons_tags(item, "printed")

            else:
                order.toggle_tag(line_id, self.tag)

        for undo_command in self.disabled_commands:
            undo_command.enable()

    def remove_sons_tags(self, item, tag):
        for son in item.items:
            son.remove_tag(tag)
            if son.items:
                self.remove_sons_tags(son, tag)
