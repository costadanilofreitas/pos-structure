from typing import Dict, Any
from pos_model import Order
from _SatXmlPartBuilder import SatXmlPartBuilder


class TotalBuilder(SatXmlPartBuilder):
    
    def build_xml(self, order, context):
        # type: (Order, Dict[unicode, Any]) -> unicode

        return "<total/>"
