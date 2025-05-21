from xml.etree import cElementTree as eTree

from ._Kds import Kds


class KdsModel(object):
    def __init__(self, kds, kds_id):
        # type: (Kds, int) -> KdsModel
        self.kds = kds
        self.kds_id = kds_id

    def get_model_xml(self):
        kds_model_xml = eTree.Element("KdsModel", kdsId=str(self.kds_id))
        eTree.SubElement(kds_model_xml, "Language", name=self.kds.language)
        eTree.SubElement(kds_model_xml, "Title", name=self.kds.title)

        self.create_bump_bar_xml(kds_model_xml)
        self.create_modifiers_xml(kds_model_xml)
        self.create_views_xml(kds_model_xml)

        return kds_model_xml

    def create_bump_bar_xml(self, kds_model_xml):
        bump_bar_xml = eTree.SubElement(kds_model_xml, "BumpBar")
        
        if self.kds.bump_bar:
            self.create_bump_bar_command_xml(self.kds.bump_bar, bump_bar_xml)

    @staticmethod
    def create_bump_bar_command_xml(bump_bar, bump_bar_xml):
        name = bump_bar.name
        simulate = str(bump_bar.simulate_bump_bar)

        bump_bar_xml = eTree.SubElement(bump_bar_xml, "BumpBar", name=name, simulate=simulate)
        for command in bump_bar.commands:
            eTree.SubElement(bump_bar_xml, "Command", name=command.name, value=str.join("|", command.keys))

    def create_modifiers_xml(self, kds_model_xml):
        modifiers_xml = eTree.SubElement(kds_model_xml, "ModifierPrefixes")
        for modifier in self.kds.modifiers:
            eTree.SubElement(modifiers_xml, "Prefix", name=modifier.name, value=modifier.description)

    def create_views_xml(self, kds_model_xml):
        views_xml = eTree.SubElement(kds_model_xml, "Views")
        for view in self.kds.views:
            zoom = view.zoom_levels[view.selected_zoom]
            selected_view = str(view.selected).lower()

            view_xml = eTree.SubElement(views_xml, "View", name=view.name, selected=selected_view)
            eTree.SubElement(view_xml, "Selected", state=str(view.selected))
            eTree.SubElement(view_xml, "ProductionView", value=view.production_view)
            eTree.SubElement(view_xml, "DisplayMode", value=view.display_mode)
            self._create_layout(view_xml, zoom)
            eTree.SubElement(view_xml, "Title", value=view.title)
            self._create_cell_format(view, view_xml)
            eTree.SubElement(view_xml, "Carousel", state=str(view.carousel))
            eTree.SubElement(view_xml, "ShowItems", state=str(view.show_items))
            eTree.SubElement(view_xml, "SelectedOrderId", value=str(view.selected_order_id))
            eTree.SubElement(view_xml, "SelectedZoom", value=str(view.selected_zoom))

            settings_xml = eTree.SubElement(view_xml, "Settings")
            eTree.SubElement(settings_xml, "Setting", name="cellDoubleClick", value=view.on_double_click)
            eTree.SubElement(settings_xml, "Setting", name="onSellClick", value=view.on_sell_click)

            thresholds_xml = eTree.SubElement(view_xml, "Thresholds")
            for threshold in view.thresholds:
                eTree.SubElement(thresholds_xml, "Threshold", value=str(threshold.time) + threshold.color)

            statistics_xml = eTree.SubElement(view_xml, "Statistics")
            for statistic in view.statistics:
                eTree.SubElement(statistics_xml, "Statistic", name=statistic.name, format=statistic.format)

            if view.auto_order_command:
                time = str(view.auto_order_command.time)
                command = view.auto_order_command.command
                eTree.SubElement(view_xml, "AutoOrderCommand", time=time, command=command)

            eTree.SubElement(view_xml, "ColoredArea", area=view.colored_area.lower())
            eTree.SubElement(view_xml, "ViewWithActions", value=str(view.view_with_actions).lower())

    @staticmethod
    def _create_cell_format(view, view_xml):
        eTree.SubElement(view_xml, "CellFormat", header=view.header_text_macro, footer=view.footer_text_macro,
                         body=view.body_text_macro)

    @staticmethod
    def _create_layout(view_xml, zoom):
        eTree.SubElement(view_xml, "Layout", rows=zoom.rows, lines=zoom.lines, cols=zoom.columns,
                         fontsize=zoom.fontsize)
