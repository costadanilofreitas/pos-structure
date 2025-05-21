from typing import Optional, Union, List, Dict

from ._Comment import Comment
from ._CustomStorage import CustomStorage
from ._Item import Item
from ._ProdStates import ProdStates
from ._ProductionOrder import ProductionOrder
from ._StateEvent import StateEvent
from ._TagEvent import TagEvent
from ._TagEventType import TagEventType
from ._User import User


def find_order_item(order, item):
    # type: (ProductionOrder, Union[Item, str]) -> Optional[Item]
    if isinstance(item, Item):
        line_id = get_line_id(item)
    else:
        line_id = item
    for item in order.items:
        if get_line_id(item) == line_id:
            return item
    return None


def get_line_id(line):
    part_code = str(line.part_code)
    if hasattr(line, "original_part_code"):
        part_code = str(line.original_part_code)
    level = str(int(line.level))
    if hasattr(line, "original_level"):
        level = str(int(line.original_level))

    return str(line.line_number) + "-" + line.item_id + "-" + level + "-" + part_code


def get_current_line_id(line):
    return str(line.line_number) + "-" + line.item_id + "-" + str(int(line.level)) + "-" + str(line.part_code)


def has_tag(tags, line_id, tag):
    # type: (Dict, str, str) -> bool
    return line_id in tags and tag in tags[line_id]


def add_tag(tags, line_id, tag):
    # type: (Dict[str, List[str]], str, str) -> bool
    if line_id in tags:
        tags[line_id].append(tag)
    else:
        tags[line_id] = [tag]


def all_done(order):
    # type: (ProductionOrder) -> bool
    for item in order.items:
        if not is_item_done(item):
            return False

    return True


def is_item_done(item):
    if item.is_product() and item.qty > 0 and item.does_not_have_tag("done"):
        return False
    elif not item.is_product():
        for son in item.items:
            if not is_item_done(son):
                return False

    return True


def create_states_from_state(state):
    state_order = ["IN_PROGRESS", "STORED", "TOTALED", "PAID", "VOIDED", "ABANDONED"]

    states = []

    try:
        index = state_order.index(state)
        for state in state_order[index:]:
            states.append(state)
    except ValueError:
        pass

    return states


def is_product(item):
    # type: (Item) -> None
    return item.item_type in ("PRODUCT", "CANADD")
