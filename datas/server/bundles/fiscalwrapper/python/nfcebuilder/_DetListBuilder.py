from _ContextKeys import ContextKeys
from _NfceXmlPartBuilder import NfceXmlPartBuilder
from pos_model import Order
from typing import Dict, Any


class DetListBuilder(NfceXmlPartBuilder):

    def __init__(self,
                 det_builder):
        # type: (NfceXmlPartBuilder) -> None
        self.det_builder = det_builder

    def build_xml(self, order, context):
        # type: (Order, Dict[unicode, Any]) -> Dict
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

        return xml
