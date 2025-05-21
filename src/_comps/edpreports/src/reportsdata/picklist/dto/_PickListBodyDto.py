from typing import List  # noqa
from _PickListItem import PickListItem  # noqa


class PickListBodyDto(object):
    def __init__(self, pick_list_items):
        # type: (List[PickListItem]) -> ()
        self.pick_list_items = pick_list_items
