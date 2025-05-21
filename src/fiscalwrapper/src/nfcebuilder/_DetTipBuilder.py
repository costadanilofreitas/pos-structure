from pos_model import Order, SaleItem
from typing import Dict, Any

from _ContextKeys import ContextKeys
from _NfceXmlPartBuilder import NfceXmlPartBuilder


class DetTipBuilder(NfceXmlPartBuilder):

    def __init__(self, det_builder, tip_config):
        # type: (NfceXmlPartBuilder, dict) -> None
        self.det_builder = det_builder
        self.tip_config = tip_config

    def build_xml(self, order, context):
        # type: (Order, Dict[unicode, Any]) -> unicode
        xml = ""

        if order.tip and self.tip_config['TipCode'] and self.tip_config['TipName']:
            sale_item = SaleItem()
            sale_item.part_code = int(self.tip_config['TipCode'])
            sale_item.product_name = self.tip_config['TipName'].upper()
            sale_item.quantity = 1
            sale_item.unit_price = order.tip
            sale_item.item_price = 0

            context[ContextKeys.current_sale_item] = sale_item
            xml += self.det_builder.build_xml(order, context)

        return xml
