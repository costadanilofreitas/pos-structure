import copy
import cfgtools
from typing import List

from util import find_key_value

from ._BumpBar import BumpBar
from ._KdsView import KdsView
from ._Modifier import Modifier


def get_first_of(it, defval=None):
    return next(it, defval)


class Kds(object):
    def __init__(self, kds_config, kds_views):
        # type: (cfgtools.Group, List[KdsView]) -> None
        self.name = kds_config.name
        self.title = ''
        self.language = ''
        self.bump_bar = None
        self.modifiers = []
        self.views = []

        self.parse_kds(kds_config, kds_views)

    def parse_kds(self, kds_config, kds_views):
        self.language = find_key_value(kds_config, "Language")
        self.title = find_key_value(kds_config, "Title")

        for group in kds_config.groups:
            if group.name == 'BumpBar':
                self.bump_bar = BumpBar(group)
            elif group.name == 'ModifierPrefixes':
                self.modifiers = self.get_modifiers(group)
            elif group.name == 'Views':
                for view_group in group.groups:
                    view_name = get_first_of(x for x in view_group.keys if x.name == "ViewName").values[0]
                    view = copy.deepcopy(get_first_of(x for x in kds_views if x.name == view_name))
                    view.name = view_group.name
                    view.display_mode = get_first_of(x for x in view_group.keys if x.name == "Display").values[0]
                    view.title = get_first_of(x for x in view_group.keys if x.name == "Title").values[0]
                    self.views.append(view)

                self.views[0].selected = True


    @staticmethod
    def get_modifiers(group):
        modifiers = []
        for modifier_key in group.keys:
            modifiers.append(Modifier(modifier_key))

        return modifiers
