from _NfceXmlPartBuilder import NfceXmlPartBuilder
from pos_model import Order
from typing import Any, Dict


class TranspBuilder(NfceXmlPartBuilder):

    def __init__(self):
        pass

    def build_xml(self, order, context):
        # type: (Order, Dict[unicode, Any]) -> unicode
        # Transporte
        inner_xml = "<transp><modFrete>9</modFrete></transp>"

        return inner_xml
