import cfgtools

from util import find_key_value


class ZoomLevel(object):
    def __init__(self, group):
        # type: (cfgtools.Group) -> ZoomLevel
        self.name = ''
        self.cols = 0
        self.lines = 0
        self.rows = 0
        self.fontsize = 0

        self.parse_zoom_level(group)

    def parse_zoom_level(self, zoom_level_group):
        # type: (cfgtools.Group) -> ()
        self.name = zoom_level_group.name
        self.cols = find_key_value(zoom_level_group, "Cols", 0)
        self.lines = find_key_value(zoom_level_group, "Lines", 0)
        self.rows = find_key_value(zoom_level_group, "Rows", 0)
        self.fontsize = find_key_value(zoom_level_group, "FontSize", 0)
