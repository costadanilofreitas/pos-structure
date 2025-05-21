from enum import Enum


class CommandType(Enum):
    order = 1
    change_prod_state = 2
    toggle_tag_line = 3
    undo = 4
    refresh_view = 5
