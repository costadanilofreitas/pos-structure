from _ContextKeys import ContextKeys
from _SatXmlPartBuilder import SatXmlPartBuilder
from pos_model import Order
from typing import Dict, Any


class DetListBuilder(SatXmlPartBuilder):

    def __init__(self, det_builder, det_tip_builder):
        self.det_builder = det_builder
        self.det_tip_builder = det_tip_builder

    def build_xml(self, order, context):
        # type: (Order, Dict[unicode, Any]) -> str
        xml = ""

        context[ContextKeys.total_vbc] = 0
        context[ContextKeys.total_prod] = 0
        context[ContextKeys.total_icms] = 0
        context[ContextKeys.total_pis] = 0
        context[ContextKeys.total_cofins] = 0
        context[ContextKeys.item_no] = 1

        for sale_item in order.sale_items:
            context[ContextKeys.current_sale_item] = sale_item
            xml += self.det_builder.build_xml(order, context)
            context[ContextKeys.item_no] += 1

        xml += self.det_tip_builder.build_xml(order, context)

        return xml
