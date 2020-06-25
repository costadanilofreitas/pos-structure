from typing import Dict, Any
from pos_model import Order
from _SatXmlPartBuilder import SatXmlPartBuilder


class TotalBuilder(SatXmlPartBuilder):
    def __init__(self):
        pass

    def build_xml(self, order, context):
        # type: (Order, Dict[unicode, Any]) -> unicode

        # Totais da Venda
        xml = "<total/>"

        return xml
