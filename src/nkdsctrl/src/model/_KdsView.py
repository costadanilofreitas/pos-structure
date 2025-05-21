import cfgtools

from util import find_key_value, find_key_values

from ._Threshold import Threshold
from ._ZoomLevel import ZoomLevel
from ._AutoOrderCommand import AutoOrderCommand
from ._Statistics import Statistics


class KdsView(object):
    def __init__(self, group):
        # type: (cfgtools.Group) -> KdsView
        self.name = ''
        self.production_view = ''
        self.selected = False
        self.selected_order_id = -1
        self.display_mode = ''
        self.title = ''
        self.header_text_macro = ''
        self.body_text_macro = ''
        self.footer_text_macro = ''
        self.carousel = True
        self.on_double_click = ''
        self.on_sell_click = 'served'
        self.show_items = True
        self.zoom_levels = []
        self.selected_zoom = 0
        self.thresholds = []
        self.statistics = []
        self.auto_order_command = None
        self.colored_area = 'body'
        self.view_with_actions = True

        self.parse_kds_view(group)

    def parse_kds_view(self, view_group):
        # type: (cfgtools.Group) -> ()
        self.name = view_group.name

        self.production_view = find_key_value(view_group, "ProductionView")
        self.header_text_macro = find_key_value(view_group, "CellHeader")
        self.body_text_macro = find_key_value(view_group, "CellBody")
        self.footer_text_macro = find_key_value(view_group, "CellFooter")
        self.on_double_click = find_key_value(view_group, "CellDoubleClick")
        self.on_sell_click = find_key_value(view_group, "OnSellClick")

        self.carousel = find_key_value(view_group, "Carousel", "true").lower() == 'true'
        self.show_items = find_key_value(view_group, "ShowItems", "true").lower() == 'true'

        for group in view_group.groups:
            if group.name == 'ZoomLevels':
                self.zoom_levels = self.get_zoom_levels(group)

        for value in find_key_values(view_group, 'Thresholds'):
            self.thresholds.append(Threshold(value))

        for value in find_key_values(view_group, 'Statistics'):
            self.statistics.append(Statistics(value))

        auto_order_command_config = find_key_value(view_group, "AutoOrderCommand")
        if auto_order_command_config:
            self.auto_order_command = AutoOrderCommand(auto_order_command_config)

        colored_area_config = find_key_value(view_group, "ColoredArea")
        if colored_area_config:
            self.colored_area = colored_area_config

        self.view_with_actions = find_key_value(view_group, "ViewWithActions", "true").lower() == 'true'

    @staticmethod
    def get_zoom_levels(group):
        zoom_levels = []
        for zoom_level_group in group.groups:
            zoom_levels.append(ZoomLevel(zoom_level_group))

        return zoom_levels
